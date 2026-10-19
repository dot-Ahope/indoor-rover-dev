# 10-19 §23 오프라인 cuVSLAM — 컨테이너 안, 도메인 42, use_sim_time. 끔(/off) · 켬(/on) 프레임용 cuVSLAM 두 개를 각자 컨테이너에.
#   설정은 09-29 §9 vslam_standalone.launch.py 와 같음(Isaac 예제 값). 바꾼 것: 입력 토픽, 15 Hz 에 맞춘 jitter 문턱, IMU 융합은 인자 imu:=true|false.
import launch
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import ComposableNodeContainer
from launch_ros.descriptions import ComposableNode


def _nodes(context):
    imu = LaunchConfiguration('imu').perform(context).lower() == 'true'
    out = []
    for k in ('off', 'on'):
        vs = ComposableNode(
            name='visual_slam_node', namespace='vs_' + k, package='isaac_ros_visual_slam',
            plugin='nvidia::isaac_ros::visual_slam::VisualSlamNode',
            parameters=[{
                'use_sim_time': True,
                'enable_image_denoising': False, 'rectified_images': True, 'enable_imu_fusion': imu,
                'gyro_noise_density': 0.000244, 'gyro_random_walk': 0.000019393,
                'accel_noise_density': 0.001862, 'accel_random_walk': 0.003, 'calibration_frequency': 200.0,
                'image_jitter_threshold_ms': 80.0,
                'base_frame': 'camera_link', 'imu_frame': 'camera_gyro_optical_frame',
                'publish_odom_to_base_tf': False, 'publish_map_to_odom_tf': False,
                'enable_slam_visualization': False, 'enable_landmarks_view': False, 'enable_observations_view': False,
                'camera_optical_frames': ['camera_infra1_optical_frame', 'camera_infra2_optical_frame'],
            }],
            remappings=[
                ('visual_slam/image_0', '/%s/infra1/image_rect_raw' % k), ('visual_slam/camera_info_0', '/%s/infra1/camera_info' % k),
                ('visual_slam/image_1', '/%s/infra2/image_rect_raw' % k), ('visual_slam/camera_info_1', '/%s/infra2/camera_info' % k),
                ('visual_slam/imu', '/camera/imu'),
            ])
        out.append(ComposableNodeContainer(name='vs_%s_container' % k, namespace='', package='rclcpp_components',
                                           executable='component_container_mt', composable_node_descriptions=[vs], output='screen',
                                           parameters=[{'use_sim_time': True}]))
    return out


def generate_launch_description():
    return launch.LaunchDescription([DeclareLaunchArgument('imu', default_value='true'), OpaqueFunction(function=_nodes)])
