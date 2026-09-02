# 전체 bringup = base(agent+RSP) + sensors(camera+lidar+EKF+foxglove). systemd 등록용(Step 5).
# 주의: agent 재시작 시 보드 RESET 필요 (펌웨어 재연결 로직 부재) → 평소엔 sensors.launch.py만 재시작할 것.
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description():
    share = get_package_share_directory('rover_bringup')
    inc = lambda name: IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(share, 'launch', name)))
    return LaunchDescription([
        inc('base.launch.py'),
        TimerAction(period=5.0, actions=[inc('sensors.launch.py')]),
    ])
