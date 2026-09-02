# Intel RealSense D455f — depth/color + 내장 IMU(200Hz)
# - camera_name 'camera' → 드라이버 base 프레임 = camera_link (URDF와 이름 일치 → static TF 불필요)
# - 4.55+ 파라미터명(depth_module.depth_profile 등) 사용. 구명칭은 조용히 무시됨 (이전 프로젝트 C16)
# - unite_imu_method 1(copy): 자이로 원신호 유지. EKF는 자이로 z만 사용 (사용 근거: JETSON_SETUP_BRIEF §4-2)
# - enable_imu:=false 로 IMU 없이 기동 가능 (커널 HID 모듈 미준비 시)
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    enable_imu = LaunchConfiguration('enable_imu')
    enable_depth = LaunchConfiguration('enable_depth')
    enable_color = LaunchConfiguration('enable_color')
    return LaunchDescription([
        DeclareLaunchArgument('enable_imu', default_value='true'),
        DeclareLaunchArgument('enable_depth', default_value='true'),
        DeclareLaunchArgument('enable_color', default_value='true'),
        Node(
            package='realsense2_camera', executable='realsense2_camera_node',
            name='camera', namespace='camera', output='screen',
            parameters=[{
                'enable_depth': enable_depth,
                'enable_color': enable_color,
                'enable_infra1': False,
                'enable_infra2': False,
                'depth_module.depth_profile': '640x480x30',
                'rgb_camera.color_profile': '640x480x15',
                'align_depth.enable': False,
                'pointcloud.enable': False,
                'enable_gyro': enable_imu,
                'enable_accel': enable_imu,
                'gyro_fps': 200,
                'accel_fps': 200,
                'unite_imu_method': 1,
                'initial_reset': True,
                'publish_tf': True,
            }],
        ),
    ])
