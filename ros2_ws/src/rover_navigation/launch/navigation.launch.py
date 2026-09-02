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
