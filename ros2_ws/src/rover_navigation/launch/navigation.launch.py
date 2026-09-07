# Nav2 기동 — WT-600 로버
#
# 전제: 아래가 먼저 떠 있어야 함
#   1) base.launch.py    — micro-ROS agent (/cmd_vel 구독, /wheel_odom 발행) + robot_state_publisher
#   2) sensors.launch.py — lidar(/scan) + EKF(odom→base_link TF, /odometry/filtered)
#   3) slam.launch.py    — slam_toolbox (map→odom TF + /map)
#      → AMCL·map_server 는 slam_toolbox 가 대신하므로 여기서 띄우지 않는다.
#
# 실행: ros2 launch rover_navigation navigation.launch.py
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    params = os.path.join(
        get_package_share_directory('rover_navigation'), 'config', 'nav2_params.yaml')
    nav2_launch = os.path.join(
        get_package_share_directory('nav2_bringup'), 'launch', 'navigation_launch.py')

    return LaunchDescription([
        DeclareLaunchArgument('params_file', default_value=params,
                              description='Nav2 파라미터 파일'),
        DeclareLaunchArgument('use_sim_time', default_value='false'),
        DeclareLaunchArgument('autostart', default_value='true',
                              description='lifecycle 노드 자동 활성화'),
        # rover-level 정체/접촉 감시 (2026-09-07). 펌웨어 스톨은 '휠 정지'만 잡으므로 트랙이 헛도는
        # 벽 밀림·긁힘은 여기서 잡는다(라이다 스캔·자이로로 실제 이동 관측). 기본 shadow(로그만) —
        # 실주행 오탐 검증 후 stuck_shadow:=false 로 취소·정지 권한 부여.
        DeclareLaunchArgument('stuck_shadow', default_value='true',
                              description='stuck_monitor 관찰 전용 모드'),
        Node(package='rover_bringup', executable='stuck_monitor.py', name='stuck_monitor',
             output='screen',
             parameters=[{'shadow_mode': LaunchConfiguration('stuck_shadow')}]),
        # controller/planner/smoother/behavior/bt_navigator/waypoint_follower
        # /velocity_smoother + lifecycle_manager 를 한 번에 기동 (상류 검증된 런치 재사용)
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(nav2_launch),
            launch_arguments={
                'use_sim_time': LaunchConfiguration('use_sim_time'),
                'params_file': LaunchConfiguration('params_file'),
                'autostart': LaunchConfiguration('autostart'),
            }.items()),
    ])
