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
                # 2026-09-09: 200 → 100Hz. CPU 부족이 EKF 주기 위반(91회, 평균 0.055s 최대 0.197s)을
                #   낳고, 늦어진 odom→base TF 때문에 slam 의 메시지 필터가 스캔을 **전부 폐기**해
                #   map→odom 이 아예 발행되지 않았다(주행 2건 실패). 200Hz 를 파이썬 컨디셔너가
                #   중계하는 구조라 그 자체로 CPU 35% 를 먹는다.
                #   0.08m/s 로 움직이는 로버에 200Hz 자이로는 과하다. EKF 는 30Hz 로 돈다.
                #   ⚠ 되돌릴 때는 sensor_conditioner CPU 와 EKF 주기 위반 횟수를 함께 볼 것.
                # ⚠ gyro 는 200 으로 되돌림. 100 을 요청했으나 D455 자이로가 지원하지 않아
                #   드라이버가 200 으로 되돌렸다("Open profile: Gyro FPS: 200"). 지원 프로파일을
                #   확인하지 않고 값을 넣은 것이 실수. accel 은 100 이 적용됐다("Accel FPS: 100").
                #   unite_imu_method 1(copy) 이라 /camera/camera/imu 는 gyro 속도(200Hz)를 따른다.
                #   → CPU 절감은 sensor_conditioner 쪽 다운샘플로 해야 한다(Phase S 항목).
                'gyro_fps': 200,
                'accel_fps': 100,
                'unite_imu_method': 1,
                'initial_reset': True,
                'publish_tf': True,
            }],
        ),
        # (2026-09-08 오전) depthimage_to_laserscan 수평 띠 방식은 철회: 10cm 상자가 0.66m 이내로 오면 띠(높이 0.12~0.16m@0.3m)
        #   아래로 내려가 마킹이 끊기고, 2D 소거 광선이 상자 셀을 지움. → 포인트클라우드 + VoxelLayer(3D 소거)로 대체.
        # (2026-09-14) 깊이 점군 릴레이: 카메라 0.45 m 안 점(근거리 아티팩트 0.36~0.38 m, 정지 30 s 에 17 % 프레임)과
        #   5 cm 복셀당 3점 미만의 고립점(상자 실루엣 비산점, 프레임당 2~4점·고립 98~99 %)을 제거해 /camera/depth/points_filtered 로.
        #   STVL 이 이 토픽을 본다. 근거: Docs/debug_log/2026-09-14/SUMMARY.md §2.5·§2.7. 드라이버엔 min_distance 필터가 없다.
        Node(
            package='rover_bringup', executable='depth_relay.py', name='depth_relay', output='screen',
            parameters=[{'min_range': 0.45, 'voxel': 0.05, 'min_points_per_voxel': 3}],
        ),
    ])
