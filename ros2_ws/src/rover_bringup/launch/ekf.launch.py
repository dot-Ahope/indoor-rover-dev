# robot_localization EKF — /odometry/filtered 30Hz + odom→base_link TF
# base.launch.py와 별도 실행 가능 (agent 재시작 없이 EKF만 재시작하기 위함)
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    config = os.path.join(
        get_package_share_directory('rover_bringup'), 'config', 'ekf.yaml')

    # 2026-09-28: conditioner:=cpp|py — C++ 이식판이 V1(출력 비트 동일)·V2(CPU 42→7 %) 통과해 기본 cpp (SUMMARY 09-28 §11). 되돌리기 = conditioner:=py
    cond = LaunchConfiguration('conditioner')
    # 2026-09-29: B2(회전축 속도 보정)·B3(회전 구간 분산) 라이브 시험용 스위치 — C++ 노드만(파라미터는 시작 때 한 번 읽음).
    #   기본 false = 09-28 §27 과 같음. 채택(새 회전 시험 통과) 뒤 기본값을 바꾼다.
    b23 = [{'icr_enable': ParameterValue(LaunchConfiguration('icr'), value_type=bool),
            'rot_cov_enable': ParameterValue(LaunchConfiguration('rot_cov'), value_type=bool)}]
    remap = [('/imu/data_raw', '/camera/camera/imu')]   # IMU 소스 = D455f 내장 IMU (보드 /imu/data_raw 는 자이로 무반응 → 미사용)
    return LaunchDescription([
        DeclareLaunchArgument('conditioner', default_value='cpp', description='sensor_conditioner 구현: cpp | py'),
        DeclareLaunchArgument('icr', default_value='false', description='B2 회전축 속도 보정 (cpp 만)'),
        DeclareLaunchArgument('rot_cov', default_value='false', description='B3 회전 구간 vx·vy 분산 확대 (cpp 만)'),
        Node(
            package='rover_bringup',
            executable='sensor_conditioner.py',
            name='sensor_conditioner',
            output='screen',
            remappings=remap,
            condition=IfCondition(PythonExpression(["'", cond, "' == 'py'"])),
        ),
        Node(
            package='rover_bringup',
            executable='sensor_conditioner_node',
            name='sensor_conditioner',
            output='screen',
            remappings=remap,
            parameters=b23,
            condition=IfCondition(PythonExpression(["'", cond, "' == 'cpp'"])),
        ),
        Node(
            package='robot_localization',
            executable='ekf_node',
            name='ekf_filter_node',
            output='screen',
            parameters=[config],
        ),
    ])
