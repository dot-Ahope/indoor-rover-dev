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
             # 2026-09-09: 2000000 → 460800. 보드 usart.c 의 override 와 반드시 일치해야 한다.
             # 사유: 흐름제어 없는 CH340 이 2 Mbps 유입을 USB 로 못 빼내 FIFO 오버런 →
             #      큰 프레임(/wheel_odom 732 B) 유실. 실수요 22.4 kB/s 대비 460800 은 2배 여유.
             'serial', '--dev', '/dev/rover', '-b', '460800'],
        output='screen',
    )

    description = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(
            get_package_share_directory('rover_description'),
            'launch', 'description.launch.py')))

    return LaunchDescription([agent, description])
