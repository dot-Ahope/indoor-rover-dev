# Nav2 기동 — WT-600 로버
#
# 전제: 아래가 먼저 떠 있어야 함
#   1) base.launch.py    — micro-ROS agent (/cmd_vel 구독, /wheel_odom 발행) + robot_state_publisher
#   2) sensors.launch.py — lidar(/scan) + EKF(odom→base_link TF, /odometry/filtered)
#   3) slam.launch.py    — slam_toolbox (map→odom TF + /map)
#      → AMCL·map_server 는 slam_toolbox 가 대신하므로 여기서 띄우지 않는다.
#      (2026-10-01 F1-4: AMCL 로 위치 추정할 때는 3) 대신 rover_navigation/localization.launch.py)
#
# 실행: ros2 launch rover_navigation navigation.launch.py [camera_layer:=nvblox|stvl] [stuck_shadow:=true]
#
# 2026-09-22 N6-0: 로컬 코스트맵의 카메라 층을 launch 인자 camera_layer 로 고른다(기본 nvblox — N5 결정).
#   - nav2_params.yaml 의 local_costmap·global_costmap(N6-1) plugins 줄을 인자대로 바꿔 /tmp/nav2_params_active.yaml 로 쓰고 Nav2 에 넘긴다
#     (원본 파일은 건드리지 않는다. 설치 YAML 을 sed 로 바꾸던 job488 방식은 폐기).
#   - nvblox 이면 nvblox.launch.py(컨테이너 안 nvblox_node, scripts/nvblox_up.sh)를 함께 띄운다. 이 launch 가 죽으면 노드도 정리된다.
#   - prep(job240)이 Nav2 를 재기동하면 nvblox 도 같이 재시작되므로 "EKF 재기동 뒤 nvblox 재시작" 규칙(절차 v2.0 §4-9)이 자동으로 지켜진다.
import os
import yaml
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, IncludeLaunchDescription, OpaqueFunction, SetEnvironmentVariable, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


# 2026-09-09: FastDDS 공유메모리 전송 비활성화 (config/fastdds_udp_only.xml 주석 참조).
#   SHM 고아 잠금 파일 때문에 프로세스는 살아있는데 퍼블리셔가 DDS 그래프에서 사라지는 사고가
#   같은 날 2회(ekf_node / slam_toolbox) 발생해 주행 2건을 잃었다. 원인 자체를 제거한다.
_FASTDDS_XML = os.path.join(
    get_package_share_directory('rover_bringup'), 'config', 'fastdds_udp_only.xml')

_LOCAL_PLUGINS = {
    'stvl': ['stvl_layer', 'obstacle_layer', 'inflation_layer'],
    'nvblox': ['nvblox_layer', 'obstacle_layer', 'inflation_layer'],
}
# 2026-09-22 N6-1: 전역 코스트맵의 카메라 층도 같은 인자로 바꾼다(STVL·depth_relay 를 경로에서 빼 CPU 회수).
_GLOBAL_PLUGINS = {
    'stvl': ['static_layer', 'stvl_layer', 'obstacle_layer', 'inflation_layer'],
    # 2026-10-01 §8.24: 전역에서 nvblox 층 제거(로컬은 유지). 카메라 유령(아무것도 없는 통로 입구에 93 칸, 기억 ≈ 81 s)이
    #   전역 계획을 막아 책상 통로 세 곳을 차례로 닫았다(f2a8, 10-01 §8.22~8.23). 낮은 물체는 로컬 nvblox 층 → MPPI 가 피한다.
    'nvblox': ['static_layer', 'obstacle_layer', 'inflation_layer'],
}
_ACTIVE_PARAMS = '/tmp/nav2_params_active.yaml'


def _make_active_params(context):
    """camera_layer 인자대로 local_costmap plugins 를 바꾼 파라미터 파일을 만들고 Nav2·nvblox 를 띄운다."""
    layer = LaunchConfiguration('camera_layer').perform(context)
    src = LaunchConfiguration('params_file').perform(context)
    if layer not in _LOCAL_PLUGINS:
        raise RuntimeError('camera_layer 는 stvl|nvblox 중 하나: %s' % layer)
    with open(src, encoding='utf-8') as f:
        params = yaml.safe_load(f)
    params['local_costmap']['local_costmap']['ros__parameters']['plugins'] = _LOCAL_PLUGINS[layer]
    params['global_costmap']['global_costmap']['ros__parameters']['plugins'] = _GLOBAL_PLUGINS[layer]
    # 2026-10-01 §8.33: nav_map:=<저장 지도 yaml> 이면 전역 정적 층을 그 지도(map_server → /map_nav)로.
    #   왜: slam_toolbox 위치 추정 모드가 주행 중 스캔을 넣어 /map 을 다시 그려(10 s 마다), 그때 본 사람·물체가 '정적 지도' 로 들어가
    #   서쪽 통로를 막았다(f2a10, 10-01 §8.32: 31.7 s 에 통로 띠 점유 31 셀 생김). 실시간 물체는 라이다 obstacle 층(지워짐)이 맡는다.
    nav_map = LaunchConfiguration('nav_map').perform(context).strip()
    if nav_map:
        params['global_costmap']['global_costmap']['ros__parameters']['static_layer']['map_topic'] = '/map_nav'
    with open(_ACTIVE_PARAMS, 'w', encoding='utf-8') as f:
        f.write('# 자동 생성(navigation.launch.py, camera_layer=%s) — 원본 %s\n' % (layer, src))
        yaml.safe_dump(params, f, allow_unicode=True, sort_keys=False)
    nav2_launch = os.path.join(
        get_package_share_directory('nav2_bringup'), 'launch', 'navigation_launch.py')
    actions = [
        # controller/planner/smoother/behavior/bt_navigator/waypoint_follower
        # /velocity_smoother + lifecycle_manager 를 한 번에 기동 (상류 검증된 런치 재사용)
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(nav2_launch),
            launch_arguments={
                'use_sim_time': LaunchConfiguration('use_sim_time'),
                'params_file': _ACTIVE_PARAMS,
                'autostart': LaunchConfiguration('autostart'),
            }.items()),
    ]
    if nav_map:
        actions += [
            Node(package='nav2_map_server', executable='map_server', name='nav_map_server', output='screen',
                 parameters=[{'yaml_filename': nav_map, 'use_sim_time': False}], remappings=[('map', '/map_nav')]),
            Node(package='nav2_lifecycle_manager', executable='lifecycle_manager', name='lifecycle_manager_navmap', output='screen',
                 parameters=[{'use_sim_time': False, 'autostart': True, 'node_names': ['nav_map_server']}]),
        ]
    if layer == 'nvblox':
        actions.append(IncludeLaunchDescription(PythonLaunchDescriptionSource(os.path.join(
            get_package_share_directory('rover_navigation'), 'launch', 'nvblox.launch.py'))))
    # 2026-09-23 N6-2 C1: 카메라 점군 생성(realsense-ros neon 필터 `pointcloud__neon_.enable`)은 스택에서는 STVL 만 쓰지만,
    #   **시험 코스의 게이트 D·E·F 와 주행 러너의 상자 모델이 점군을 입력으로 쓴다** — 끄면 상자 검출이 비어 주행이 거부된다(09-23 §7).
    #   그래서 기본은 'keep'(건드리지 않음). camera_pointcloud:=off 는 계측 없는 운용에서만(정지 CPU −6 %p: 릴레이 3.7→0, realsense 15.3→13.9).
    #   모드 S 로 되돌릴 때는 항상 true. 카메라 노드는 sensors.launch 소속이라 파라미터만 만진다(15 s 뒤).
    pcl = LaunchConfiguration('camera_pointcloud').perform(context)
    if layer == 'stvl' or pcl == 'off':
        actions.append(TimerAction(period=15.0, actions=[ExecuteProcess(
            cmd=['ros2', 'param', 'set', '/camera/camera', 'pointcloud__neon_.enable', 'false' if (layer == 'nvblox' and pcl == 'off') else 'true'],
            name='camera_pointcloud_' + layer, output='screen')]))
    return actions


def generate_launch_description():
    params = os.path.join(
        get_package_share_directory('rover_navigation'), 'config', 'nav2_params.yaml')

    return LaunchDescription([
        SetEnvironmentVariable('FASTRTPS_DEFAULT_PROFILES_FILE', _FASTDDS_XML),
        DeclareLaunchArgument('params_file', default_value=params,
                              description='Nav2 파라미터 원본 파일(plugins 줄은 camera_layer 로 덮어씀)'),
        DeclareLaunchArgument('camera_layer', default_value='nvblox',
                              description='로컬 코스트맵 카메라 층: nvblox(기본, 2026-09-22 N5 채택) | stvl(Phase S 기준선 구성)'),
        DeclareLaunchArgument('camera_pointcloud', default_value='keep',
                              description="keep(기본: 점군 유지 — 게이트·러너가 씀) | off(모드 N 운용 전용, 계측 불가)"),
        DeclareLaunchArgument('use_sim_time', default_value='false'),
        DeclareLaunchArgument('nav_map', default_value='',
                              description='전역 정적 층에 쓸 저장 지도 yaml(비우면 slam_toolbox /map). 10-01 §8.33'),
        DeclareLaunchArgument('autostart', default_value='true',
                              description='lifecycle 노드 자동 활성화'),
        # rover-level 정체/접촉 감시 (2026-09-07). 펌웨어 스톨은 '휠 정지'만 잡으므로 트랙이 헛도는
        # 벽 밀림·긁힘은 여기서 잡는다(라이다 스캔·자이로로 실제 이동 관측).
        # 2026-09-08 활성(기본 false): 실주행 오탐 0 (09-07 46s + 09-08 6회 주행) · 정탐 3/3 (job57) 검증 완료.
        # 관찰만 하려면 stuck_shadow:=true.
        DeclareLaunchArgument('stuck_shadow', default_value='false',
                              description='stuck_monitor 관찰 전용 모드'),
        Node(package='rover_bringup', executable='stuck_monitor.py', name='stuck_monitor',
             output='screen',
             parameters=[{'shadow_mode': LaunchConfiguration('stuck_shadow')}]),
        # 온보드 목표 시간·무진행 한도 (2026-09-29, Docs/debug_log/2026-09-29/SUMMARY.md §13 L2): PC 러너·Wi-Fi 없이도
        # 한도를 넘은 목표를 취소·정지. Nav2 진행 검사기(0.25 m/25 s)보다 느슨한 최후 방어선. 끄려면 nav_guard:=false.
        DeclareLaunchArgument('nav_guard', default_value='true', description='온보드 목표 시간·무진행 한도'),
        Node(package='rover_bringup', executable='nav_guard.py', name='nav_guard', output='screen',
             condition=IfCondition(LaunchConfiguration('nav_guard'))),
        OpaqueFunction(function=_make_active_params),
    ])
