# 기본 bringup: micro-ros-agent (Docker) + robot_state_publisher
# 주의: 이 launch가 agent를 직접 띄우므로, 별도 microros_agent 컨테이너가 떠 있으면 안 됨
#       (같은 컨테이너 이름을 써서 이중 실행을 차단한다).
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import ExecuteProcess, IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


# 2026-09-09: FastDDS 공유메모리 전송 비활성화 (config/fastdds_udp_only.xml 주석 참조).
#   SHM 고아 잠금 파일 때문에 프로세스는 살아있는데 퍼블리셔가 DDS 그래프에서 사라지는 사고가
#   같은 날 2회(ekf_node / slam_toolbox) 발생해 주행 2건을 잃었다. 원인 자체를 제거한다.
_FASTDDS_XML = os.path.join(
    get_package_share_directory('rover_bringup'), 'config', 'fastdds_udp_only.xml')


def generate_launch_description():
    # /dev/rover 심볼릭 링크를 실장치로 resolve (docker --device에는 실장치 경로 전달)
    rover_dev = os.path.realpath('/dev/rover')

    agent = ExecuteProcess(
        cmd=['docker', 'run', '--rm', '--name', 'microros_agent',
             '--net', 'host',
             # 2026-09-16: 에이전트의 DDS 참가자도 루프백 고정 프로파일을 쓴다(호스트 노드와 같은 XML 을 마운트).
             #   안 하면 에이전트는 Wi-Fi IP 를 광고하고 호스트 노드는 127.0.0.1 만 쓰므로 /cmd_vel 이 보드에 못 간다.
             '-v', f'{_FASTDDS_XML}:/fastdds_udp_only.xml:ro',
             '-e', 'FASTRTPS_DEFAULT_PROFILES_FILE=/fastdds_udp_only.xml',
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

    # 2026-09-28: 보드 OLED 에 Wi-Fi IP·SSID 표시 — Jetson 이 /rover/display_info 로 3 s 마다 보냄(scripts/display_info_pub.py)
    display_info = Node(package='rover_bringup', executable='display_info_pub.py', name='display_info_pub', output='log')

    return LaunchDescription([
        SetEnvironmentVariable('FASTRTPS_DEFAULT_PROFILES_FILE', _FASTDDS_XML), agent, description, display_info])
