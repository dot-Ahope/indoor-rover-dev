# robot_state_publisher — 기본: 저장소 확정본 Docs/02_hardware/rover.urdf (WT-600, 2026-08-27) 그대로 로드.
# use_xacro:=true 이면 rover.urdf.xacro(데크 메시·실측 인자) 사용 — 실험용, 확정본은 rover.urdf.
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def _spawn(context):
    share = get_package_share_directory('rover_description')
    if LaunchConfiguration('use_xacro').perform(context) == 'true':
        import xacro
        desc = xacro.process_file(os.path.join(share, 'urdf', 'rover.urdf.xacro')).toxml()
    else:
        with open(os.path.join(share, 'urdf', 'rover.urdf'), 'r') as f:
            desc = f.read()
    return [Node(
        package='robot_state_publisher', executable='robot_state_publisher',
        name='robot_state_publisher', output='screen',
        parameters=[{'robot_description': desc}],
    )]


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument('use_xacro', default_value='false'),
        OpaqueFunction(function=_spawn),
    ])
