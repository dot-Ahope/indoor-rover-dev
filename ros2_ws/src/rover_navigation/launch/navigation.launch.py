# Nav2 기동 — WT-600 로버
#
# 전제: 아래가 먼저 떠 있어야 함
#   1) base.launch.py    — micro-ROS agent (/cmd_vel 구독, /wheel_odom 발행) + robot_state_publisher
#   2) sensors.launch.py — lidar(/scan) + EKF(odom→base_link TF, /odometry/filtered)
#   3) slam.launch.py    — slam_toolbox (map→odom TF + /map)
#      → AMCL·map_server 는 slam_toolbox 가 대신하므로 여기서 띄우지 않는다.
#      (2026-10-01 F1-4: AMCL 로 위치 추정할 때는 3) 대신 rover_navigation/localization.launch.py)
#
# 실행: ros2 launch rover_navigation navigation.launch.py [camera_layer:=nvblox|stvl] [stuck_shadow:=true]
#
# 2026-09-22 N6-0: 로컬 코스트맵의 카메라 층을 launch 인자 camera_layer 로 고른다(기본 nvblox — N5 결정).
#   - nav2_params.yaml 의 local_costmap·global_costmap(N6-1) plugins 줄을 인자대로 바꿔 /tmp/nav2_params_active.yaml 로 쓰고 Nav2 에 넘긴다
#     (원본 파일은 건드리지 않는다. 설치 YAML 을 sed 로 바꾸던 job488 방식은 폐기).
#   - nvblox 이면 nvblox.launch.py(컨테이너 안 nvblox_node, scripts/nvblox_up.sh)를 함께 띄운다. 이 launch 가 죽으면 노드도 정리된다.
#   - prep(job240)이 Nav2 를 재기동하면 nvblox 도 같이 재시작되므로 "EKF 재기동 뒤 nvblox 재시작" 규칙(절차 v2.0 §4-9)이 자동으로 지켜진다.
import os
import yaml
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, IncludeLaunchDescription, OpaqueFunction, SetEnvironmentVariable, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


# 2026-09-09: FastDDS 공유메모리 전송 비활성화 (config/fastdds_udp_only.xml 주석 참조).
#   SHM 고아 잠금 파일 때문에 프로세스는 살아있는데 퍼블리셔가 DDS 그래프에서 사라지는 사고가
#   같은 날 2회(ekf_node / slam_toolbox) 발생해 주행 2건을 잃었다. 원인 자체를 제거한다.
_FASTDDS_XML = os.path.join(
    get_package_share_directory('rover_bringup'), 'config', 'fastdds_udp_only.xml')

_LOCAL_PLUGINS = {
    'stvl': ['stvl_layer', 'obstacle_layer', 'inflation_layer'],
    'nvblox': ['nvblox_layer', 'obstacle_layer', 'inflation_layer'],
}
# 2026-09-22 N6-1: 전역 코스트맵의 카메라 층도 같은 인자로 바꾼다(STVL·depth_relay 를 경로에서 빼 CPU 회수).
_GLOBAL_PLUGINS = {
    'stvl': ['static_layer', 'stvl_layer', 'obstacle_layer', 'inflation_layer'],
    # 2026-10-01 §8.24: 전역에서 nvblox 층 제거(로컬은 유지). 카메라 유령(아무것도 없는 통로 입구에 93 칸, 기억 ≈ 81 s)이
    #   전역 계획을 막아 책상 통로 세 곳을 차례로 닫았다(f2a8, 10-01 §8.22~8.23). 낮은 물체는 로컬 nvblox 층 → MPPI 가 피한다.
    'nvblox': ['static_layer', 'obstacle_layer', 'inflation_layer'],
}
_ACTIVE_PARAMS = '/tmp/nav2_params_active.yaml'


def _make_active_params(context):
    """camera_layer 인자대로 local_costmap plugins 를 바꾼 파라미터 파일을 만들고 Nav2·nvblox 를 띄운다."""
    layer = LaunchConfiguration('camera_layer').perform(context)
    src = LaunchConfiguration('params_file').perform(context)
    if layer not in _LOCAL_PLUGINS:
        raise RuntimeError('camera_layer 는 stvl|nvblox 중 하나: %s' % layer)
    with open(src, encoding='utf-8') as f:
        params = yaml.safe_load(f)
    params['local_costmap']['local_costmap']['ros__parameters']['plugins'] = _LOCAL_PLUGINS[layer]
    params['global_costmap']['global_costmap']['ros__parameters']['plugins'] = _GLOBAL_PLUGINS[layer]
    # 2026-10-01 §8.33: nav_map:=<저장 지도 yaml> 이면 전역 정적 층을 그 지도(map_server → /map_nav)로.
    #   왜: slam_toolbox 위치 추정 모드가 주행 중 스캔을 넣어 /map 을 다시 그려(10 s 마다), 그때 본 사람·물체가 '정적 지도' 로 들어가
    #   서쪽 통로를 막았다(f2a10, 10-01 §8.32: 31.7 s 에 통로 띠 점유 31 셀 생김). 실시간 물체는 라이다 obstacle 층(지워짐)이 맡는다.
    # 2026-10-02 §12: local_frame:=map 이면 로컬 코스트맵(과 nvblox 층의 변환 대상)을 map 좌표에 그린다(기본 odom).
    #   왜: 제자리 회전 중 실제 미끄러짐(±90°×3 에 32 cm)을 EKF 는 0.3 cm 로 봐서, odom 좌표 로컬 코스트맵에 옛 표시가 어긋나 쌓였다
    #   (10-02 §11.1: 근거 없는 치명 칸 4 → 95, f2b3 에선 벽이 12 cm 두꺼워져 MPPI 실패). SLAM 은 그 미끄러짐을 본다(0.322 m).
    #   대가: 위치 추정 보정 때마다 로컬 표시가 계단식으로 이동, 큰 점프면 통째로 이동. A/B 시험용 인자로 먼저 둔다.
    local_frame = LaunchConfiguration('local_frame').perform(context).strip() or 'odom'
    lp = params['local_costmap']['local_costmap']['ros__parameters']
    lp['global_frame'] = local_frame
    lp.setdefault('nvblox_layer', {})['nav2_costmap_global_frame'] = local_frame
    nav_map = LaunchConfiguration('nav_map').perform(context).strip()
    if nav_map:
        params['global_costmap']['global_costmap']['ros__parameters']['static_layer']['map_topic'] = '/map_nav'
    # 2026-10-07 §8.2: global_camera:=stvl 이면 전역의 카메라를 라이다와 한 격자(obstacle_layer)에서 빼 STVL 3D 층으로.
    #   왜: 한 격자에선 라이다(0.185 m) 2D 소거가 빔 아래 낮은 상자(카메라만 봄)를 매 스캔 지움 → 가까이 가면 상자를 잊고 밀거나(f2c2)
    #   계획·MPPI 가 엇갈려 정체(f2d2). 사용자 조건: '화각 밖에선 기억, 카메라가 보고 있을 땐 갱신'(동적 물체를 계속 기억하면 못 감).
    #   STVL: 표시 = 깊이점(0.06~0.40 m, 1.2 m 안), 기억 = voxel_decay(긴 수명), 갱신 = 깊이 절두체 안에서만 가속 감쇠로 소거.
    #   절두체 근평면 min_z 는 실측 깊이 끊김(0.45~0.65 m, 장면마다 다름 — 09-09·09-10 에 근평면을 너무 가깝게 둬 보이지 않는 상자를 2~3 s 에 지움)
    #   보다 넉넉히 0.8 m. 감쇠 가속: 선형 수명 T 에서 절두체 안 t 초 뒤 소거 ≈ √(T/a)(09-10: T 30·a 3 → 2~3 s 실측) → T 600·a 100 ≈ 2.4 s.
    gcam = LaunchConfiguration('global_camera').perform(context).strip() or 'obstacle'
    if gcam == 'stvl':
        gp = params['global_costmap']['global_costmap']['ros__parameters']
        gp['plugins'] = ['static_layer', 'stvl_layer', 'obstacle_layer', 'inflation_layer']
        gp['obstacle_layer']['observation_sources'] = 'scan'                 # 라이다만 — 카메라 칸을 못 지움(별도 격자)
        sv = gp['stvl_layer']; sv['voxel_decay'] = 600.0; sv['decay_model'] = 0
        # §8.3 정정: 원 STVL 블록의 track_unknown_space true 를 그대로 쓰니 카메라가 아직 못 본 곳을 '미지' 로 덮어(최대값 결합)
        #   정적 지도의 빈 공간까지 가림(출발 방 대부분 −1). 전역 카메라 층은 본 것만 표시 → false.
        sv['track_unknown_space'] = False
        sv['depth_clear']['min_z'] = 0.8; sv['depth_clear']['decay_acceleration'] = 100.0
    elif gcam != 'obstacle':
        raise RuntimeError('global_camera 는 obstacle|stvl 중 하나: %s' % gcam)
    # 2026-10-07 §11 (사용자): 장기 주행에서만 MPPI 후보 궤적·최적 궤적(/trajectories MarkerArray)·변환 경로(/transformed_global_plan) 발행.
    #   왜: 경로를 '계획하는 모습' 을 시각화하려면 매 주기 예측이 필요. 평소엔 끔 — 09-17 mp7: 기본 간격이면 ≈5 MB/s 기록·15 W CPU 압박.
    #   간격을 넓혀 부담을 줄임: 후보 1000 개 중 20 개마다 1 개(50 개), 시간 2 스텝마다.
    if LaunchConfiguration('mppi_viz').perform(context).strip().lower() in ('1', 'true', 'yes'):
        mp = params['controller_server']['ros__parameters']['FollowPathMPPI']
        mp['visualize'] = True; mp.setdefault('TrajectoryVisualizer', {}).update({'trajectory_step': 20, 'time_step': 2})
    with open(_ACTIVE_PARAMS, 'w', encoding='utf-8') as f:
        f.write('# 자동 생성(navigation.launch.py, camera_layer=%s, global_camera=%s) — 원본 %s\n' % (layer, gcam, src))
        yaml.safe_dump(params, f, allow_unicode=True, sort_keys=False)
    nav2_launch = os.path.join(
        get_package_share_directory('nav2_bringup'), 'launch', 'navigation_launch.py')
    actions = [
        # controller/planner/smoother/behavior/bt_navigator/waypoint_follower
        # /velocity_smoother + lifecycle_manager 를 한 번에 기동 (상류 검증된 런치 재사용)
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(nav2_launch),
            launch_arguments={
                'use_sim_time': LaunchConfiguration('use_sim_time'),
                'params_file': _ACTIVE_PARAMS,
                'autostart': LaunchConfiguration('autostart'),
            }.items()),
    ]
    if nav_map:
        actions += [
            Node(package='nav2_map_server', executable='map_server', name='nav_map_server', output='screen',
                 parameters=[{'yaml_filename': nav_map, 'use_sim_time': False}], remappings=[('map', '/map_nav')]),
            Node(package='nav2_lifecycle_manager', executable='lifecycle_manager', name='lifecycle_manager_navmap', output='screen',
                 parameters=[{'use_sim_time': False, 'autostart': True, 'node_names': ['nav_map_server']}]),
        ]
    if layer == 'nvblox':
        actions.append(IncludeLaunchDescription(PythonLaunchDescriptionSource(os.path.join(
            get_package_share_directory('rover_navigation'), 'launch', 'nvblox.launch.py'))))
    # 2026-09-23 N6-2 C1: 카메라 점군 생성(realsense-ros neon 필터 `pointcloud__neon_.enable`)은 스택에서는 STVL 만 쓰지만,
    #   **시험 코스의 게이트 D·E·F 와 주행 러너의 상자 모델이 점군을 입력으로 쓴다** — 끄면 상자 검출이 비어 주행이 거부된다(09-23 §7).
    #   그래서 기본은 'keep'(건드리지 않음). camera_pointcloud:=off 는 계측 없는 운용에서만(정지 CPU −6 %p: 릴레이 3.7→0, realsense 15.3→13.9).
    #   모드 S 로 되돌릴 때는 항상 true. 카메라 노드는 sensors.launch 소속이라 파라미터만 만진다(15 s 뒤).
    pcl = LaunchConfiguration('camera_pointcloud').perform(context)
    if layer == 'stvl' or pcl == 'off':
        actions.append(TimerAction(period=15.0, actions=[ExecuteProcess(
            cmd=['ros2', 'param', 'set', '/camera/camera', 'pointcloud__neon_.enable', 'false' if (layer == 'nvblox' and pcl == 'off') else 'true'],
            name='camera_pointcloud_' + layer, output='screen')]))
    return actions


def generate_launch_description():
    params = os.path.join(
        get_package_share_directory('rover_navigation'), 'config', 'nav2_params.yaml')

    return LaunchDescription([
        SetEnvironmentVariable('FASTRTPS_DEFAULT_PROFILES_FILE', _FASTDDS_XML),
        DeclareLaunchArgument('params_file', default_value=params,
                              description='Nav2 파라미터 원본 파일(plugins 줄은 camera_layer 로 덮어씀)'),
        DeclareLaunchArgument('camera_layer', default_value='nvblox',
                              description='로컬 코스트맵 카메라 층: nvblox(기본, 2026-09-22 N5 채택) | stvl(Phase S 기준선 구성)'),
        DeclareLaunchArgument('camera_pointcloud', default_value='keep',
                              description="keep(기본: 점군 유지 — 게이트·러너가 씀) | off(모드 N 운용 전용, 계측 불가)"),
        DeclareLaunchArgument('use_sim_time', default_value='false'),
        DeclareLaunchArgument('mppi_viz', default_value='false',
                              description='장기 주행 기록용 MPPI 후보·최적 궤적 발행(10-07 §11, 기본 끔)'),
        DeclareLaunchArgument('global_camera', default_value='obstacle',
                              description='전역 카메라 표시: obstacle(라이다와 한 격자, 10-01 §8.35) | stvl(별도 3D 층, 화각 밖 기억·절두체 안 갱신, 10-07 §8.2)'),
        DeclareLaunchArgument('nav_map', default_value='',
                              description='전역 정적 층에 쓸 저장 지도 yaml(비우면 slam_toolbox /map). 10-01 §8.33'),
        DeclareLaunchArgument('local_frame', default_value='odom',
                              description='로컬 코스트맵 좌표계: odom(기본) | map(10-02 §12 A/B)'),
        DeclareLaunchArgument('autostart', default_value='true',
                              description='lifecycle 노드 자동 활성화'),
        # rover-level 정체/접촉 감시 (2026-09-07). 펌웨어 스톨은 '휠 정지'만 잡으므로 트랙이 헛도는
        # 벽 밀림·긁힘은 여기서 잡는다(라이다 스캔·자이로로 실제 이동 관측).
        # 2026-09-08 활성(기본 false): 실주행 오탐 0 (09-07 46s + 09-08 6회 주행) · 정탐 3/3 (job57) 검증 완료.
        # 관찰만 하려면 stuck_shadow:=true.
        DeclareLaunchArgument('stuck_shadow', default_value='false',
                              description='stuck_monitor 관찰 전용 모드'),
        Node(package='rover_bringup', executable='stuck_monitor.py', name='stuck_monitor',
             output='screen',
             parameters=[{'shadow_mode': LaunchConfiguration('stuck_shadow')}]),
        # 온보드 목표 시간·무진행 한도 (2026-09-29, Docs/debug_log/2026-09-29/SUMMARY.md §13 L2): PC 러너·Wi-Fi 없이도
        # 한도를 넘은 목표를 취소·정지. Nav2 진행 검사기(0.25 m/25 s)보다 느슨한 최후 방어선. 끄려면 nav_guard:=false.
        DeclareLaunchArgument('nav_guard', default_value='true', description='온보드 목표 시간·무진행 한도'),
        Node(package='rover_bringup', executable='nav_guard.py', name='nav_guard', output='screen',
             condition=IfCondition(LaunchConfiguration('nav_guard'))),
        OpaqueFunction(function=_make_active_params),
    ])
