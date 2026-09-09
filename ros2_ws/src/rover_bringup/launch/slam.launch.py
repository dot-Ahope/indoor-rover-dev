# slam_toolbox online async — 선행: /scan(lidar.launch.py) + odom→base_link(ekf.launch.py) + RSP
# 맵 저장: ros2 run nav2_map_server map_saver_cli -f <name>
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import SetEnvironmentVariable
from launch_ros.actions import Node


# 2026-09-09: FastDDS 공유메모리 전송 비활성화 (config/fastdds_udp_only.xml 주석 참조).
#   SHM 고아 잠금 파일 때문에 프로세스는 살아있는데 퍼블리셔가 DDS 그래프에서 사라지는 사고가
#   같은 날 2회(ekf_node / slam_toolbox) 발생해 주행 2건을 잃었다. 원인 자체를 제거한다.
_FASTDDS_XML = os.path.join(
    get_package_share_directory('rover_bringup'), 'config', 'fastdds_udp_only.xml')


def generate_launch_description():
    config = os.path.join(get_package_share_directory('rover_bringup'), 'config', 'slam.yaml')
    return LaunchDescription([
        SetEnvironmentVariable('FASTRTPS_DEFAULT_PROFILES_FILE', _FASTDDS_XML),
        Node(
            package='slam_toolbox', executable='async_slam_toolbox_node',
            name='slam_toolbox', output='screen',
            parameters=[config],
        ),
    ])
