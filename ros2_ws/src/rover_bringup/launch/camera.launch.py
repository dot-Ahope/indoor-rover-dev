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
        # ── depth → 가상 LaserScan (N1.5, 2026-09-08) ──
        # 목적: S2L 평면 아래의 낮은 장애물·라이다 사각 보완을 코스트맵에 공급.
        # 포인트클라우드(640×480×18Hz ≈ 5.5M pt/s) 대신 깊이 이미지 수평 띠만 쓰는 이유: CPU.
        # 기하(카메라 z=0.143m, 수평 장착, D455 fy≈385px @640×480):
        #   scan_height 50 → 중심행 ±25px → 광선 피치 ±3.7° → 거리 d 에서 높이 0.143 ± d·tan3.7°
        #   = 1.0m 에서 0.08~0.21m, 1.5m 에서 0.05~0.24m. 바닥은 최하 광선이 0.143/tan3.7° = 2.2m 밖에서만
        #   맞으므로 range_max 1.5m 이면 바닥 오탐 없음(피치 오차 1°당 바닥 접점 ±0.5m 여유).
        # 출력 프레임: camera_depth_frame (x 전방, realsense 가 TF 발행). 코스트맵은 TF 로 base_link 변환.
        Node(
            package='depthimage_to_laserscan', executable='depthimage_to_laserscan_node',
            name='depth_scan', output='screen',
            remappings=[('depth', '/camera/camera/depth/image_rect_raw'),
                        ('depth_camera_info', '/camera/camera/depth/camera_info'),
                        ('scan', '/camera/scan')],
            parameters=[{'scan_height': 50, 'range_min': 0.30, 'range_max': 1.50,
                         'scan_time': 0.054, 'output_frame': 'camera_depth_frame'}],
        ),
    ])
