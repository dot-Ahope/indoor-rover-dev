# 10-21 §18 3번 정지 시험 nv1 — NVIDIA 권장 구성 그대로: RealSense 드라이버(4.51.1-isaac) + realsense_splitter + cuVSLAM 을 한 component container 에.
#   새 이미지 컨테이너(isaac_rs_test) 안에서 실행. 카메라 설정 = nvblox 예제 realsense_emitter_flashing.yaml(깊이 · IR 640×480×60, 프로젝터 번갈이, 점군 끔, IMU 200/200 unite 2)
#   다른 것: camera_name 'camera'(지금 스택 토픽 이름 /camera/camera/... 유지), cuVSLAM 은 지금 그림자 설정(IMU 융합 끔) + 입력 = 분리 노드의 끈 IR, QoS SENSOR_DATA.
import os
import launch
from launch_ros.actions import ComposableNodeContainer
from launch_ros.descriptions import ComposableNode

YAML = '/workspaces/isaac_ros-dev/src/isaac_ros_nvblox/nvblox_examples/nvblox_examples_bringup/config/sensors/realsense_emitter_flashing.yaml'
C = '/camera'   # 4.51.1 은 토픽에 노드 이름이 안 붙음(/camera/depth/...) — 4.54+ 의 /camera/camera/... 와 다름(§18.1)
SP = '/camera/realsense_splitter_node/output'


def generate_launch_description():
    # NV_MODE=off: 같은 드라이버 · 같은 장면의 대조 — 프로젝터 상시 끔, 깊이 · IR 640×480×30(번갈이 때 각 30 과 같은 주기)
    off = os.environ.get('NV_MODE', 'flash') == 'off'
    over = {'camera_name': 'camera'}
    if off:
        over.update({'depth_module.emitter_enabled': 0, 'depth_module.emitter_on_off': False, 'depth_module.profile': '640x480x30'})
    cam = ComposableNode(namespace='camera', name='camera', package='realsense2_camera', plugin='realsense2_camera::RealSenseNodeFactory',
                         parameters=[YAML, over])
    spl = ComposableNode(namespace='camera', name='realsense_splitter_node', package='realsense_splitter', plugin='nvblox::RealsenseSplitterNode',
                         parameters=[{'input_qos': 'SENSOR_DATA', 'output_qos': 'SENSOR_DATA'}],
                         remappings=[('input/infra_1', C + '/infra1/image_rect_raw'), ('input/infra_1_metadata', C + '/infra1/metadata'),
                                     ('input/infra_2', C + '/infra2/image_rect_raw'), ('input/infra_2_metadata', C + '/infra2/metadata'),
                                     ('input/depth', C + '/depth/image_rect_raw'), ('input/depth_metadata', C + '/depth/metadata'),
                                     ('input/pointcloud', C + '/depth/color/points'), ('input/pointcloud_metadata', C + '/depth/metadata')])
    vs = ComposableNode(name='visual_slam_node', namespace='', package='isaac_ros_visual_slam', plugin='nvidia::isaac_ros::visual_slam::VisualSlamNode',
                        parameters=[{'enable_image_denoising': False, 'rectified_images': True, 'enable_imu_fusion': False,
                                     'image_jitter_threshold_ms': 50.0,   # 끈 IR 30 Hz(33 ms) 기준
                                     'image_qos': 'SENSOR_DATA', 'imu_qos': 'SENSOR_DATA',
                                     'base_frame': 'camera_link', 'imu_frame': 'camera_gyro_optical_frame',
                                     'publish_odom_to_base_tf': False, 'publish_map_to_odom_tf': False,
                                     'enable_slam_visualization': False, 'enable_landmarks_view': False, 'enable_observations_view': False,
                                     'camera_optical_frames': ['camera_infra1_optical_frame', 'camera_infra2_optical_frame']}],
                        remappings=[('visual_slam/image_0', SP + '/infra_1'), ('visual_slam/camera_info_0', C + '/infra1/camera_info'),
                                    ('visual_slam/image_1', SP + '/infra_2'), ('visual_slam/camera_info_1', C + '/infra2/camera_info'),
                                    ('visual_slam/imu', C + '/imu')])
    return launch.LaunchDescription([ComposableNodeContainer(
        name='nv_static_container', namespace='', package='rclcpp_components', executable='component_container_mt',
        composable_node_descriptions=[cam, spl, vs], output='screen')])
