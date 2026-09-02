# 기본 bringup: micro-ros-agent (Docker) + robot_state_publisher
# 주의: 이 launch가 agent를 직접 띄우므로, 별도 microros_agent 컨테이너가 떠 있으면 안 됨
#       (같은 컨테이너 이름을 써서 이중 실행을 차단한다).
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import ExecuteProcess, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description():
    # /dev/rover 심볼릭 링크를 실장치로 resolve (docker --device에는 실장치 경로 전달)
    rover_dev = os.path.realpath('/dev/rover')

    agent = ExecuteProcess(
        cmd=['docker', 'run', '--rm', '--name', 'microros_agent',
             '--net', 'host',
             '--device', f'{rover_dev}:/dev/rover',
             'microros/micro-ros-agent:humble',
             'serial', '--dev', '/dev/rover', '-b', '2000000'],
        output='screen',
    )

    description = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(
            get_package_share_directory('rover_description'),
            'launch', 'description.launch.py')))

    return LaunchDescription([agent, description])
