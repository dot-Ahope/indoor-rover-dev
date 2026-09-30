# 조이스틱 teleop — joy_linux_node(/dev/input/js0 → /joy) + teleop_twist_joy(/joy → /cmd_vel)
# 매핑·안전: config/joy_teleop.yaml (axis1=전후 양수전진, axis2=좌우 양수좌회전, 데드존 정지)
# 실행: ros2 launch rover_bringup joy_teleop.launch.py
# ⚠ 데드맨 버튼 없음(패드 버튼 미작동) → 스틱 놓으면 중립=정지. 감독 하에 저속 주행.
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


# 2026-09-30: profile:=mapping — F1 매핑용 저속(직진 0.07 m/s·회전 0.3 rad/s). 빠른 회전은 트랙 밀림을 키워
#   지도 품질을 떨어뜨린다(09-28 회전 시험: 180° 당 10~27 cm). 기본(normal)은 yaml 값(0.10·0.8).
_PROFILES = {'mapping': {'scale_linear.x': 0.07, 'scale_angular.yaw': 0.3}}


def _make(context):
    cfg = os.path.join(get_package_share_directory('rover_bringup'), 'config', 'joy_teleop.yaml')
    over = _PROFILES.get(LaunchConfiguration('profile').perform(context), {})
    return [
        Node(
            package='joy_linux', executable='joy_linux_node', name='joy_node',
            output='screen', parameters=[cfg],
        ),
        Node(
            package='teleop_twist_joy', executable='teleop_node', name='teleop_twist_joy_node',
            output='screen', parameters=[cfg, over],
        ),
    ]


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument('profile', default_value='normal', description='normal | mapping(저속)'),
        OpaqueFunction(function=_make),
    ])
