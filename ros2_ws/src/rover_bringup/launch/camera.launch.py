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
                'depth_module.depth_profile': '640x480x15',   # 2026-09-08 30→15fps (포인트클라우드 CPU)
                'rgb_camera.color_profile': '640x480x15',
                'align_depth.enable': False,
                # 2026-09-08 N1.5: 포인트클라우드 ON + 데시메이션 ×4 (640×480 → 160×120 = 19.2k pt/frame @15fps)
                #   → Nav2 VoxelLayer 가 실제 높이로 마킹/3D 소거. 바닥은 min_obstacle_height 로 배제.
                # ⚠ 파라미터 이름이 빌드마다 다름: Jetson(ARM/NEON) 의 realsense-ros 4.58.3 은 처리블록 이름이
                #   "pointcloud (neon)" 이라 'pointcloud__neon_.*' 로 노출됨(09-08 ros2 param list 로 확인). x86 은 'pointcloud.*'.
                #   모르는 이름은 조용히 무시되므로 둘 다 적는다.
                'pointcloud.enable': True,
                'pointcloud__neon_.enable': True,
                'pointcloud__neon_.allow_no_texture_points': True,
                'decimation_filter.enable': True,
                'decimation_filter.filter_magnitude': 4,
                'enable_gyro': enable_imu,
                'enable_accel': enable_imu,
                'gyro_fps': 200,
                'accel_fps': 200,
                'unite_imu_method': 1,
                'initial_reset': True,
                'publish_tf': True,
            }],
        ),
        # (2026-09-08 오전) depthimage_to_laserscan 수평 띠 방식은 철회: 10cm 상자가 0.66m 이내로 오면 띠(높이 0.12~0.16m@0.3m)
        #   아래로 내려가 마킹이 끊기고, 2D 소거 광선이 상자 셀을 지움. → 포인트클라우드 + VoxelLayer(3D 소거)로 대체.
    ])
