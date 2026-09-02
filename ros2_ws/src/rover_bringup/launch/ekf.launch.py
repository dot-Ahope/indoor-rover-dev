# robot_localization EKF — /odometry/filtered 30Hz + odom→base_link TF
# base.launch.py와 별도 실행 가능 (agent 재시작 없이 EKF만 재시작하기 위함)
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    config = os.path.join(
        get_package_share_directory('rover_bringup'), 'config', 'ekf.yaml')

    return LaunchDescription([
        Node(
            package='rover_bringup',
            executable='sensor_conditioner.py',
            name='sensor_conditioner',
            output='screen',
            # IMU 소스 = D455f 내장 IMU (보드 /imu/data_raw 는 자이로 무반응 → 미사용)
            remappings=[('/imu/data_raw', '/camera/camera/imu')],
        ),
        Node(
            package='robot_localization',
            executable='ekf_node',
            name='ekf_filter_node',
            output='screen',
            parameters=[config],
        ),
    ])
