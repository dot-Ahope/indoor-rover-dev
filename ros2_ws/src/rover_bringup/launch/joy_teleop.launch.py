# 조이스틱 teleop — joy_linux_node(/dev/input/js0 → /joy) + teleop_twist_joy(/joy → /cmd_vel)
# 매핑·안전: config/joy_teleop.yaml (axis1=전후 양수전진, axis2=좌우 양수좌회전, 데드존 정지)
# 실행: ros2 launch rover_bringup joy_teleop.launch.py
# ⚠ 데드맨 버튼 없음(패드 버튼 미작동) → 스틱 놓으면 중립=정지. 감독 하에 저속 주행.
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    cfg = os.path.join(get_package_share_directory('rover_bringup'), 'config', 'joy_teleop.yaml')
    return LaunchDescription([
        Node(
            package='joy_linux', executable='joy_linux_node', name='joy_node',
            output='screen', parameters=[cfg],
        ),
        Node(
            package='teleop_twist_joy', executable='teleop_node', name='teleop_twist_joy_node',
            output='screen', parameters=[cfg],
        ),
    ])
