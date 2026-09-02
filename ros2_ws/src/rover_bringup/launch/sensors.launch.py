# 센서 측 통합 launch: camera(D455f) + lidar(S2L) + EKF(+conditioner) + foxglove_bridge
# base.launch.py(agent+RSP)와 분리 — 센서/EKF만 재시작해도 micro-ROS 세션(보드 리셋 필요)을 건드리지 않음
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    share = get_package_share_directory('rover_bringup')
    inc = lambda name, args=None: IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(share, 'launch', name)),
        launch_arguments=(args or {}).items())
    return LaunchDescription([
        DeclareLaunchArgument('enable_depth', default_value='true'),
        DeclareLaunchArgument('enable_color', default_value='true'),
        DeclareLaunchArgument('enable_imu', default_value='true'),
        inc('camera.launch.py', {
            'enable_depth': LaunchConfiguration('enable_depth'),
            'enable_color': LaunchConfiguration('enable_color'),
            'enable_imu': LaunchConfiguration('enable_imu')}),
        inc('lidar.launch.py'),
        inc('foxglove.launch.py'),
        # EKF는 카메라 IMU가 흐른 뒤 기동 (컨디셔너 바이어스 캘리브레이션 10s가 카메라 초기화 후 시작되도록)
        TimerAction(period=8.0, actions=[inc('ekf.launch.py')]),
    ])
