# robot_localization EKF — /odometry/filtered 30Hz + odom→base_link TF
# base.launch.py와 별도 실행 가능 (agent 재시작 없이 EKF만 재시작하기 위함)
import os

import yaml
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def _truthy(context, name):
    return LaunchConfiguration(name).perform(context).strip().lower() in ('1', 'true', 'yes')


def _nodes(context):
    share = get_package_share_directory('rover_bringup')
    config = os.path.join(share, 'config', 'ekf.yaml')
    cond = LaunchConfiguration('conditioner').perform(context).strip()
    rf2o = _truthy(context, 'rf2o')
    st = {'use_sim_time': _truthy(context, 'use_sim_time')}   # bag 재생 검증용(기본 false)
    shadow = _truthy(context, 'shadow') and rf2o
    remap = [('/imu/data_raw', '/camera/camera/imu')]   # IMU 소스 = D455f 내장 IMU (보드 /imu/data_raw 는 자이로 무반응 → 미사용)

    # 2026-09-28: conditioner:=cpp|py — C++ 이식판이 V1(출력 비트 동일)·V2(CPU 42→7 %) 통과해 기본 cpp (SUMMARY 09-28 §11). 되돌리기 = conditioner:=py
    # 2026-09-29: B2(회전축 속도 보정)·B3(회전 구간 분산) 라이브 시험용 스위치 — C++ 노드만(파라미터는 시작 때 한 번 읽음). 기본 false.
    cp = {'icr_enable': _truthy(context, 'icr'), 'rot_cov_enable': _truthy(context, 'rot_cov')}
    # 2026-10-06 R3: rf2o:=true 면 B3 를 켜고 순수 회전 중 휠 병진 σ 를 0.3 으로 — 휠의 '옆 이동 0'(25 Hz)이 rf2o(10 Hz)를 눌러
    #   회전 미끄러짐을 지우지 않게(10-02 §14.1: σ 0.03 이면 rot3 36.8 cm 중 7 cm 만 잡음, 0.3 이면 줄자 대비 4.3 cm).
    if rf2o:
        cp.update({'rot_cov_enable': True, 'rot_vx_var': 0.3 ** 2, 'rot_vy_var': 0.3 ** 2})
    acts = [
        Node(package='rover_bringup', executable='sensor_conditioner.py', name='sensor_conditioner', output='screen', remappings=remap, parameters=[st])
        if cond == 'py' else
        Node(package='rover_bringup', executable='sensor_conditioner_node', name='sensor_conditioner', output='screen',
             remappings=remap, parameters=[cp, st]),
    ]
    if cond == 'py' and rf2o:
        raise RuntimeError('rf2o:=true 는 conditioner:=cpp 만(B3 공분산이 C++ 판에만 있음)')

    ekf = [config, st]
    if rf2o:
        # odom1 = rf2o 게이트 출력(차체 vx·vy 만). 회전은 자이로(imu0)가 담당 — rf2o 각도 누적은 540° 에 4~8° 로 자이로보다 나쁨(§13.1)
        ekf.append({'odom1': '/odom_rf2o/gated',
                    'odom1_config': [False] * 6 + [True, True, False] + [False] * 6,
                    'odom1_queue_size': 10, 'odom1_nodelay': True, 'odom1_differential': False, 'odom1_relative': False})
        acts += [
            Node(package='rf2o_laser_odometry', executable='rf2o_laser_odometry_node', name='rf2o_laser_odometry', output='screen',
                 parameters=[os.path.join(share, 'config', 'rf2o.yaml'), st]),
            Node(package='rover_bringup', executable='rf2o_gate.py', name='rf2o_gate', output='screen',
                 parameters=[{'relay_plain': shadow, 'csv': LaunchConfiguration('gate_csv').perform(context),
                              'gyro_source': LaunchConfiguration('gate_src').perform(context),
                              'q_mode': LaunchConfiguration('gate_q').perform(context),
                              'v_mode': LaunchConfiguration('gate_v').perform(context)}, st]),
        ]
    acts.append(Node(package='robot_localization', executable='ekf_node', name='ekf_filter_node', output='screen', parameters=ekf))
    if shadow:
        # 비교용 그림자 EKF A(rf2o 넣기 전 구성 그대로, TF 안 냄) — 단계별 회전 실증(§17)에서 A·B 를 같은 시각에 비교
        with open(config, encoding='utf-8') as f:
            pa = yaml.safe_load(f)['ekf_filter_node']['ros__parameters']
        pa.update({'publish_tf': False, 'odom0': '/wheel_odom/plain'}); pa.update(st)
        acts.append(Node(package='robot_localization', executable='ekf_node', name='ekf_shadow_a', output='screen',
                         parameters=[pa], remappings=[('odometry/filtered', '/odometry/ekf_a')]))
    return acts


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument('conditioner', default_value='cpp', description='sensor_conditioner 구현: cpp | py'),
        DeclareLaunchArgument('icr', default_value='false', description='B2 회전축 속도 보정 (cpp 만)'),
        DeclareLaunchArgument('rot_cov', default_value='false', description='B3 회전 구간 vx·vy 분산 확대 (cpp 만)'),
        DeclareLaunchArgument('rf2o', default_value='false',
                              description='2026-10-06 R3: rf2o 스캔 정합 속도를 게이트 거쳐 EKF 병진 입력으로(기본 끔, ~/rf2o_ws 필요)'),
        DeclareLaunchArgument('shadow', default_value='false', description='rf2o:=true 일 때 비교용 그림자 EKF A(/odometry/ekf_a) 같이 띄움'),
        DeclareLaunchArgument('gate_csv', default_value='', description='rf2o 게이트 판정 기록 csv 경로(비우면 안 씀)'),
        DeclareLaunchArgument('gate_src', default_value='ekf', description='rf2o 게이트 회전 속도 기준: ekf(30 Hz, 기본) | imu(200 Hz)'),
        DeclareLaunchArgument('gate_q', default_value='off', description='rf2o 게이트 G3 품질 검사: off | log | on (10-06 §12)'),
        DeclareLaunchArgument('gate_v', default_value='off', description='rf2o 게이트 G4 회전 중 병진 타당성: off | on (10-06 §12.1)'),
        DeclareLaunchArgument('use_sim_time', default_value='false', description='bag 재생 검증용'),
        OpaqueFunction(function=_nodes),
    ])
