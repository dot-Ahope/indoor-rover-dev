# 10-21 §19 mx1 — 시험 컨테이너(isaac_rs_test, 드라이버 4.51.1 · librealsense 2.55.1 RSUSB) 안 카메라만.
#   설정 = NVIDIA realsense_emitter_flashing.yaml(번갈이), camera_name 'camera'. MX_FPS=30 이면 깊이 · IR 640x480x30(10-19 우리 번갈이 방식)
import os
import launch
from launch_ros.actions import ComposableNodeContainer
from launch_ros.descriptions import ComposableNode

YAML = '/workspaces/isaac_ros-dev/src/isaac_ros_nvblox/nvblox_examples/nvblox_examples_bringup/config/sensors/realsense_emitter_flashing.yaml'


def generate_launch_description():
    over = {'camera_name': 'camera'}
    if os.environ.get('MX_FPS', '60') == '30':
        over['depth_module.profile'] = '640x480x30'
    # §19.2 mx2: 기동 파라미터로 노출 · 게인 고정(MX_EXP · MX_GAIN), MX_OFF=1 이면 프로젝터 상시 끔 + 자동 노출(대조)
    if os.environ.get('MX_EXP'):
        over.update({'depth_module.enable_auto_exposure': False, 'depth_module.exposure': int(os.environ['MX_EXP']), 'depth_module.gain': int(os.environ['MX_GAIN'])})
    if os.environ.get('MX_OFF') == '1':
        over.update({'depth_module.emitter_enabled': 0, 'depth_module.emitter_on_off': False, 'depth_module.enable_auto_exposure': True})
    cam = ComposableNode(namespace='camera', name='camera', package='realsense2_camera', plugin='realsense2_camera::RealSenseNodeFactory',
                         parameters=[YAML, over])
    return launch.LaunchDescription([ComposableNodeContainer(
        name='mx_container', namespace='', package='rclcpp_components', executable='component_container_mt',
        composable_node_descriptions=[cam], output='screen')])
