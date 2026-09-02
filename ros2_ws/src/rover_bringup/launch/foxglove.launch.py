# foxglove_bridge — PC Foxglove Studio에서 ws://<jetson-ip>:8765 접속 (RViz 대체)
from launch import LaunchDescription
from launch_ros.actions import Node

# topic_whitelist — bridge가 서빙할 토픽을 필수만으로 제한(정규식 full-match).
#   근거(2026-09-01): 과부하된 bridge가 /tf를 클라이언트로 늦게 전달 → Foxglove에서 로봇이 4초마다 점프.
#   무거운 /camera/* (color 15Hz·depth) 를 화이트리스트에서 제외해 bridge 부하를 구조적으로 상한.
#   ⚠ 나중에 foxglove에서 카메라 영상을 보려면 여기에 '/camera/.*' 추가하거나 whitelist를 완화.
WHITELIST = [
    '/scan', '/scan_raw',
    '/map', '/map_metadata',
    '/tf', '/tf_static',
    '/robot_description',
    '/odometry/filtered', '/wheel_odom',
    '/imu/data', '/imu/data_raw',
    '/rover/status', '/battery',
    '/cmd_vel', '/joy',
]


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='foxglove_bridge', executable='foxglove_bridge', name='foxglove_bridge',
            output='screen',
            parameters=[{'port': 8765, 'address': '0.0.0.0',
                         'topic_whitelist': WHITELIST}],
        ),
    ])
