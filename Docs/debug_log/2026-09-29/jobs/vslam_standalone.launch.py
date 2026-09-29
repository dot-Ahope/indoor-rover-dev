# 09-29 §9 cuVSLAM 3.2 단독 확인용 (컨테이너 안에서 실행). Isaac 예제 isaac_ros_visual_slam_realsense.launch.py 의 노드 파라미터를
#   그대로 쓰되: 카메라는 호스트에서 따로 띄움(/camera/camera/*), 30 fps 에 맞춘 jitter, 기존 TF 와 충돌하지 않게 TF 발행 끔.
import launch
from launch_ros.actions import ComposableNodeContainer
from launch_ros.descriptions import ComposableNode


def generate_launch_description():
    vslam = ComposableNode(
        name='visual_slam_node', package='isaac_ros_visual_slam',
        plugin='nvidia::isaac_ros::visual_slam::VisualSlamNode',
        parameters=[{
            'enable_image_denoising': False,
            'rectified_images': True,
            'enable_imu_fusion': True,
            'gyro_noise_density': 0.000244,
            'gyro_random_walk': 0.000019393,
            'accel_noise_density': 0.001862,
            'accel_random_walk': 0.003,
            'calibration_frequency': 200.0,
            'image_jitter_threshold_ms': 35.0,
            'base_frame': 'camera_link',
            'imu_frame': 'camera_gyro_optical_frame',
            'publish_odom_to_base_tf': False,
            'publish_map_to_odom_tf': False,
            'enable_slam_visualization': False,
            'enable_landmarks_view': False,
            'enable_observations_view': False,
            'camera_optical_frames': ['camera_infra1_optical_frame', 'camera_infra2_optical_frame'],
        }],
        remappings=[
            ('visual_slam/image_0', '/camera/camera/infra1/image_rect_raw'),
            ('visual_slam/camera_info_0', '/camera/camera/infra1/camera_info'),
            ('visual_slam/image_1', '/camera/camera/infra2/image_rect_raw'),
            ('visual_slam/camera_info_1', '/camera/camera/infra2/camera_info'),
            ('visual_slam/imu', '/camera/camera/imu'),
        ],
    )
    return launch.LaunchDescription([ComposableNodeContainer(
        name='visual_slam_launch_container', namespace='', package='rclcpp_components',
        executable='component_container', composable_node_descriptions=[vslam], output='screen')])
