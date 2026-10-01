# AMCL 위치 추정 — F1-4 후보 ③ (2026-10-01)
#   map_server(격자 지도 pgm/yaml) + amcl + lifecycle_manager_localization.
#   slam.launch.py 대신 띄운다(둘 다 map→odom 을 내면 안 됨). 나머지(base·sensors·navigation)는 그대로.
# 실행: ros2 launch rover_navigation localization.launch.py map:=/home/jetson/maps/office/office_v2.yaml
# 근거·비교: Docs/debug_log/2026-10-01/SUMMARY.md §7
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, SetEnvironmentVariable
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

_FASTDDS_XML = os.path.join(
    get_package_share_directory('rover_bringup'), 'config', 'fastdds_udp_only.xml')


def generate_launch_description():
    params = os.path.join(get_package_share_directory('rover_navigation'), 'config', 'amcl.yaml')
    return LaunchDescription([
        SetEnvironmentVariable('FASTRTPS_DEFAULT_PROFILES_FILE', _FASTDDS_XML),
        DeclareLaunchArgument('map', description='격자 지도 yaml 경로'),
        Node(package='nav2_map_server', executable='map_server', name='map_server', output='screen',
             parameters=[params, {'yaml_filename': LaunchConfiguration('map')}]),
        Node(package='nav2_amcl', executable='amcl', name='amcl', output='screen', parameters=[params]),
        Node(package='nav2_lifecycle_manager', executable='lifecycle_manager', name='lifecycle_manager_localization',
             output='screen',
             parameters=[{'use_sim_time': False, 'autostart': True, 'node_names': ['map_server', 'amcl']}]),
    ])
