# 센서 측 통합 launch: camera(D455f) + lidar(S2L) + EKF(+conditioner) + foxglove_bridge
# base.launch.py(agent+RSP)와 분리 — 센서/EKF만 재시작해도 micro-ROS 세션(보드 리셋 필요)을 건드리지 않음
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, TimerAction, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


# 2026-09-09: FastDDS 공유메모리 전송 비활성화 (config/fastdds_udp_only.xml 주석 참조).
#   SHM 고아 잠금 파일 때문에 프로세스는 살아있는데 퍼블리셔가 DDS 그래프에서 사라지는 사고가
#   같은 날 2회(ekf_node / slam_toolbox) 발생해 주행 2건을 잃었다. 원인 자체를 제거한다.
_FASTDDS_XML = os.path.join(
    get_package_share_directory('rover_bringup'), 'config', 'fastdds_udp_only.xml')


def generate_launch_description():
    share = get_package_share_directory('rover_bringup')
    inc = lambda name, args=None: IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(share, 'launch', name)),
        launch_arguments=(args or {}).items())
    return LaunchDescription([
        SetEnvironmentVariable('FASTRTPS_DEFAULT_PROFILES_FILE', _FASTDDS_XML),
        DeclareLaunchArgument('enable_depth', default_value='true'),
        DeclareLaunchArgument('enable_color', default_value='true'),
        DeclareLaunchArgument('enable_imu', default_value='true'),
        # foxglove 로 내보낼 토픽 범위 (2026-09-09): lean(기본) | full | cam
        DeclareLaunchArgument('viz', default_value='lean'),
        inc('camera.launch.py', {
            'enable_depth': LaunchConfiguration('enable_depth'),
            'enable_color': LaunchConfiguration('enable_color'),
            'enable_imu': LaunchConfiguration('enable_imu')}),
        inc('lidar.launch.py'),
        inc('foxglove.launch.py', {'viz': LaunchConfiguration('viz')}),
        # EKF는 카메라 IMU가 흐른 뒤 기동 (컨디셔너 바이어스 캘리브레이션 10s가 카메라 초기화 후 시작되도록)
        TimerAction(period=8.0, actions=[inc('ekf.launch.py')]),
    ])
