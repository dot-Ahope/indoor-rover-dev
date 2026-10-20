# Intel RealSense D455f — depth/color + 내장 IMU(200Hz)
# - camera_name 'camera' → 드라이버 base 프레임 = camera_link (URDF와 이름 일치 → static TF 불필요)
# - 4.55+ 파라미터명(depth_module.depth_profile 등) 사용. 구명칭은 조용히 무시됨 (이전 프로젝트 C16)
# - unite_imu_method 1(copy): 자이로 원신호 유지. EKF는 자이로 z만 사용 (사용 근거: JETSON_SETUP_BRIEF §4-2)
# - enable_imu:=false 로 IMU 없이 기동 가능 (커널 HID 모듈 미준비 시)
# - (2026-10-19 §16) emitter_flash:=true — 프로젝터 프레임마다 켬/끔(cuVSLAM 용 점 무늬 없는 IR + nvblox 용 켬 깊이, 09-29 §10 O1).
#   깊이 · IR 640×480×stereo_fps(기본 30 → 켬 15 · 끔 15 = 지금 깊이 주기와 같음), 드라이버 영상은 /camera/raw/... 로 옮기고
#   emitter_splitter_node 가 켬 깊이 · 점군과 끔 IR 을 원래 이름(/camera/camera/...)으로 내보낸다 → nvblox · depth_relay · 러너는 그대로.
#   기본 false = 지금까지와 같은 구성. 근거·시험 Docs/debug_log/2026-10-19/SUMMARY.md §15~
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import ComposableNodeContainer, Node
from launch_ros.descriptions import ComposableNode

RAW = '/camera/raw'


def _camera(context):
    enable_imu = LaunchConfiguration('enable_imu')
    enable_depth = LaunchConfiguration('enable_depth')
    enable_color = LaunchConfiguration('enable_color')
    flash = LaunchConfiguration('emitter_flash').perform(context).lower() in ('1', 'true', 'on')
    # (10-19 §25) emitter_off:=true — 프로젝터 상시 끔 + IR 좌우 켬(같은 15 fps). cuVSLAM 오프라인 확인용 기록 주행.
    #   깊이는 수동 스테레오(무늬 없는 면에 구멍 — 09-29 M1) → 카메라만 보는 낮은 물체는 놓칠 수 있다. 원시 IR 만 /camera/raw 로 옮겨 분리 노드가 기록.
    eoff = LaunchConfiguration('emitter_off').perform(context).lower() in ('1', 'true', 'on')
    fps = int(LaunchConfiguration('stereo_fps').perform(context))
    stereo = {'enable_infra1': False, 'enable_infra2': False,
              'depth_module.depth_profile': '640x480x15'}   # 2026-09-08 30→15fps (포인트클라우드 CPU)
    remaps = []
    if eoff and not flash:
        stereo = {'enable_infra1': True, 'enable_infra2': True, 'depth_module.depth_profile': '640x480x15', 'depth_module.infra_profile': '640x480x15',
                  'depth_module.emitter_enabled': 0}
        remaps = [('/camera/camera/%s' % t, '%s/%s' % (RAW, t)) for t in ('infra1/image_rect_raw', 'infra2/image_rect_raw')]
    if flash:
        prof = '640x480x%d' % fps
        stereo = {'enable_infra1': True, 'enable_infra2': True, 'depth_module.depth_profile': prof, 'depth_module.infra_profile': prof,
                  'depth_module.emitter_enabled': 1, 'depth_module.emitter_on_off': True}
        # 영상 · 점군만 옮긴다(camera_info · metadata 는 원래 이름 — 소비자는 stamp 로 짝을 맞추고, 분리 노드는 원래 metadata 를 본다)
        remaps = [('/camera/camera/%s' % t, '%s/%s' % (RAW, t)) for t in
                  ('depth/image_rect_raw', 'infra1/image_rect_raw', 'infra2/image_rect_raw', 'depth/color/points')]
    cam_params = {
        'enable_depth': enable_depth,
        'enable_color': enable_color,
        **stereo,
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
        'decimation_filter.enable': int(LaunchConfiguration('decimation').perform(context)) > 1,
        # 10-20 §8: decimation:= 인자(기본 4 = 지금). 4 이상은 4×4 블록 '0 아닌 값 평균'(2~3 은 중앙값 — librealsense 설명, 기억 · 시험으로 확인 중)이라
        #   상자 모서리에서 상자 · 배경 깊이가 섞인 점이 면 밖에 찍히는지(10-20 §8.1 북 면 +6 cm) 정지 A/B 로 본다. 1 = 데시메이션 끔(640×480).
        'decimation_filter.filter_magnitude': int(LaunchConfiguration('decimation').perform(context)),
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
    }
    if not flash and not eoff:
        return [Node(package='realsense2_camera', executable='realsense2_camera_node',
                     name='camera', namespace='camera', output='screen', parameters=[cam_params])]
    # 10-19 §17: 번갈이면 드라이버와 분리 노드를 한 component container 에 — 원시 영상이 프로세스 밖(UDP)으로 나가지 않게(§16 S2: 30 Hz 중
    #   21 Hz 만 도착). 컨테이너 이름에 realsense2_camera 를 넣어 러너 · prep 의 프로세스 검사(pgrep realsense2_camera = 1)와 정리 패턴이 그대로 맞게.
    #   멀티스레드 실행기: 드라이버 콜백과 분리 노드가 서로 기다리지 않게(분리 노드 콜백끼리는 기본 콜백 그룹이라 동시에 안 돎).
    return [ComposableNodeContainer(
        name='realsense2_camera_container', namespace='camera', package='rclcpp_components', executable='component_container_mt',
        output='screen',
        composable_node_descriptions=[
            ComposableNode(package='realsense2_camera', plugin='realsense2_camera::RealSenseNodeFactory',
                           name='camera', namespace='camera', parameters=[cam_params], remappings=remaps),
            ComposableNode(package='rover_bringup', plugin='rover_bringup::EmitterSplitter', name='emitter_splitter', namespace='',
                           parameters=[{'in_ns': RAW, 'meta_ns': '/camera/camera', 'out_ns': '/camera/camera'} if flash else
                                       # 상시 끔: 깊이 · 점군은 드라이버가 원래 이름으로 직접 — 분리 노드는 원시 IR 기록만(나눈 IR 출력은 쓰지 않는 이름으로)
                                       {'in_ns': RAW, 'meta_ns': '/camera/camera', 'out_ns': '/camera/split_unused', 'split_points': False}]),
        ])]


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument('enable_imu', default_value='true'),
        DeclareLaunchArgument('enable_depth', default_value='true'),
        DeclareLaunchArgument('enable_color', default_value='true'),
        DeclareLaunchArgument('emitter_flash', default_value='false'),
        DeclareLaunchArgument('stereo_fps', default_value='30'),
        DeclareLaunchArgument('emitter_off', default_value='false'),
        DeclareLaunchArgument('decimation', default_value='4', description='10-20 §8 깊이 데시메이션 배율(4 = 지금, 2, 1 = 끔) — 점군 크기도 같이 바뀜'),
        OpaqueFunction(function=_camera),
        # (2026-09-08 오전) depthimage_to_laserscan 수평 띠 방식은 철회: 10cm 상자가 0.66m 이내로 오면 띠(높이 0.12~0.16m@0.3m)
        #   아래로 내려가 마킹이 끊기고, 2D 소거 광선이 상자 셀을 지움. → 포인트클라우드 + VoxelLayer(3D 소거)로 대체.
        # (2026-09-14) 깊이 점군 릴레이: 카메라 0.45 m 안 점(근거리 아티팩트 0.36~0.38 m, 정지 30 s 에 17 % 프레임)과
        #   5 cm 복셀당 3점 미만의 고립점(상자 실루엣 비산점, 프레임당 2~4점·고립 98~99 %)을 제거해 /camera/depth/points_filtered 로.
        #   STVL 이 이 토픽을 본다. 근거: Docs/debug_log/2026-09-14/SUMMARY.md §2.5·§2.7. 드라이버엔 min_distance 필터가 없다.
        Node(
            package='rover_bringup', executable='depth_relay.py', name='depth_relay', output='screen',
            # (2026-09-14 §2.21) persist: 최근 5프레임 중 3프레임 이상 같은 복셀에 점이 있어야 통과 — 25 % 프레임에만 찍히는 바닥 점이 영구 LETHAL 되는 것을 막는다
            parameters=[{'min_range': 0.45, 'max_range': 4.0, 'voxel': 0.05, 'min_points_per_voxel': 3, 'persist_frames': 5, 'persist_min': 3, 'process_every': 1}],
        ),
    ])
