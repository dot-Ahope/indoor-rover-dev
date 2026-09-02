# slam_toolbox online async — 선행: /scan(lidar.launch.py) + odom→base_link(ekf.launch.py) + RSP
# 맵 저장: ros2 run nav2_map_server map_saver_cli -f <name>
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    config = os.path.join(get_package_share_directory('rover_bringup'), 'config', 'slam.yaml')
    return LaunchDescription([
        Node(
            package='slam_toolbox', executable='async_slam_toolbox_node',
            name='slam_toolbox', output='screen',
            parameters=[config],
        ),
    ])
