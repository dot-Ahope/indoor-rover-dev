# nvblox 노드 기동 (N6-0, 2026-09-22) — Isaac ROS 컨테이너 안의 nvblox_node 를 scripts/nvblox_up.sh 로 띄운다.
#   navigation.launch.py 가 camera_layer:=nvblox 일 때 포함한다. 단독 실행: ros2 launch rover_navigation nvblox.launch.py
#   파라미터 채택본: config/nvblox_local.yaml (절단 2.0·감쇠 0.99, 2026-09-22 N5). 로그: /tmp/nvblox_node.log (게이트 J 가 Rates/Delays 를 읽음)
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    share = get_package_share_directory('rover_navigation')
    return LaunchDescription([
        DeclareLaunchArgument('nvblox_params', default_value=os.path.join(share, 'config', 'nvblox_local.yaml'),
                              description='nvblox 파라미터(컨테이너가 보는 /tmp 로 복사됨)'),
        DeclareLaunchArgument('nvblox_log', default_value='/tmp/nvblox_node.log'),
        ExecuteProcess(
            cmd=['bash', os.path.join(share, 'scripts', 'nvblox_up.sh'),
                 LaunchConfiguration('nvblox_params'), LaunchConfiguration('nvblox_log')],
            name='nvblox_up', output='screen', emulate_tty=False),
    ])
