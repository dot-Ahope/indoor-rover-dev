# RPLidar S2L — /scan (frame_id lidar_link). 장치: udev /dev/rplidar (CP210x 10c4:ea60)
# 파라미터 근거: 이전 프로젝트 실측(S-series 1,000,000 baud, Standard 16m/10Hz, angle_compensate)
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument('serial_port', default_value='/dev/rplidar'),
        DeclareLaunchArgument('scan_mode', default_value='Standard'),
        Node(
            package='rplidar_ros', executable='rplidar_node', name='rplidar_node',
            output='screen',
            remappings=[('/scan', '/scan_raw')],   # 원시 스캔 → 재스탬프 노드로
            parameters=[{
                'channel_type': 'serial',
                'serial_port': LaunchConfiguration('serial_port'),
                'serial_baudrate': 1000000,
                'frame_id': 'lidar_link',
                'inverted': False,
                'angle_compensate': True,
                'scan_mode': LaunchConfiguration('scan_mode'),
            }],
        ),
        # 스캔 디스큐: 각 빔을 취득시각별 자세로 보정(EKF ω 기반) → 회전 끌림/왜곡 제거. /scan_raw → /scan
        # (scan_restamp.py 는 스윕중앙 앵커만 하는 경량판 — deskew 로 대체. 필요 시 롤백 가능)
        Node(
            package='rover_bringup', executable='scan_deskew.py', name='scan_deskew',
            output='screen', parameters=[{'ref': 'end', 'omega_deadband': 0.02}],
        ),
    ])
