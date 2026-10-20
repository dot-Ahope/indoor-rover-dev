# cuVSLAM(isaac_ros_visual_slam 3.2.6) 실시간 — Isaac ROS 컨테이너 안에서 실행한다(호스트 ros2 launch 용 아님). (2026-10-20 §6)
#   cuvslam_up.sh 가 /tmp/cuvslam_active.launch.py 로 복사해 컨테이너에서 띄운다. 설정은 오프라인 검증판(10-19 jobs/vslam_offline.launch.py)과 같고
#   다른 것: 실시간(use_sim_time 끔), 입력 = 호스트 드라이버의 원시 IR(camera.launch emitter_off:=true 가 /camera/raw/... 로 옮긴 것 — 프로젝터 상시 끔),
#   IMU 융합 끔(10-20 §3.1: 켜면 불안정 yaw 7.8°).
#   출력: /visual_slam/tracking/odometry(camera_link 자세) → 호스트 vslam_twist.py 가 차체 속도로. TF 는 내지 않는다(EKF · SLAM 이 맡음).
import launch
from launch_ros.actions import ComposableNodeContainer
from launch_ros.descriptions import ComposableNode


def generate_launch_description():
    vs = ComposableNode(
        name='visual_slam_node', namespace='', package='isaac_ros_visual_slam',
        plugin='nvidia::isaac_ros::visual_slam::VisualSlamNode',
        parameters=[{
            'enable_image_denoising': False, 'rectified_images': True, 'enable_imu_fusion': False,
            'image_jitter_threshold_ms': 80.0,   # 15 fps(67 ms) 기준 — 10-19 오프라인과 같음
            'base_frame': 'camera_link', 'imu_frame': 'camera_gyro_optical_frame',
            'publish_odom_to_base_tf': False, 'publish_map_to_odom_tf': False,
            'enable_slam_visualization': False, 'enable_landmarks_view': False, 'enable_observations_view': False,
            'camera_optical_frames': ['camera_infra1_optical_frame', 'camera_infra2_optical_frame'],
        }],
        remappings=[
            ('visual_slam/image_0', '/camera/raw/infra1/image_rect_raw'), ('visual_slam/camera_info_0', '/camera/camera/infra1/camera_info'),
            ('visual_slam/image_1', '/camera/raw/infra2/image_rect_raw'), ('visual_slam/camera_info_1', '/camera/camera/infra2/camera_info'),
            ('visual_slam/imu', '/camera/camera/imu'),
        ])
    return launch.LaunchDescription([ComposableNodeContainer(
        name='cuvslam_container', namespace='', package='rclcpp_components', executable='component_container_mt',
        composable_node_descriptions=[vs], output='screen')])
