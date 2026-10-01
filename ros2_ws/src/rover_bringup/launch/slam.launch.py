# slam_toolbox online async — 선행: /scan(lidar.launch.py) + odom→base_link(ekf.launch.py) + RSP
# 맵 저장: ros2 run nav2_map_server map_saver_cli -f <name>
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, LogInfo, OpaqueFunction, SetEnvironmentVariable
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


# 2026-09-09: FastDDS 공유메모리 전송 비활성화 (config/fastdds_udp_only.xml 주석 참조).
#   SHM 고아 잠금 파일 때문에 프로세스는 살아있는데 퍼블리셔가 DDS 그래프에서 사라지는 사고가
#   같은 날 2회(ekf_node / slam_toolbox) 발생해 주행 2건을 잃었다. 원인 자체를 제거한다.
_FASTDDS_XML = os.path.join(
    get_package_share_directory('rover_bringup'), 'config', 'fastdds_udp_only.xml')

# 2026-09-28: slam_build:=fork|apt — 포크(~/slam_ws, slam_toolbox 2.6.10 + "거리 또는 회전각" 패치)를 기본으로.
#   원본(apt)은 병진 < 4.5 cm 면 스캔을 버려 스키드스티어 제자리 회전 밀림(180° 당 10~27 cm)을 못 본다.
#   근거: Docs/debug_log/2026-09-28/SUMMARY.md §3.1, §8~9 (bag 재생 11/11 포착, 오차 평균 1.1 cm), 패치 jobs/slam_toolbox_rover_fork.patch
#   포크가 없으면 apt 로 떨어지고 로그로 알린다. 되돌리기 = slam_build:=apt
_FORK_PREFIX = os.path.expanduser('~/slam_ws/install/slam_toolbox')


def _select_build(context):
    want = LaunchConfiguration('slam_build').perform(context)
    exe = os.path.join(_FORK_PREFIX, 'lib', 'slam_toolbox', 'async_slam_toolbox_node')
    if want == 'fork' and os.path.exists(exe):
        # 패키지 조회(ament index)와 공유 라이브러리가 포크를 먼저 찾도록 이 launch 프로세스 환경 앞에 붙인다(자식 프로세스가 상속)
        os.environ['AMENT_PREFIX_PATH'] = _FORK_PREFIX + os.pathsep + os.environ.get('AMENT_PREFIX_PATH', '')
        os.environ['LD_LIBRARY_PATH'] = os.path.join(_FORK_PREFIX, 'lib') + os.pathsep + os.environ.get('LD_LIBRARY_PATH', '')
        return [LogInfo(msg='[slam.launch] slam_toolbox = 포크 %s' % exe)]
    if want == 'fork':
        return [LogInfo(msg='[slam.launch] ⚠ 포크 없음(%s) → apt 판 사용' % exe)]
    return [LogInfo(msg='[slam.launch] slam_toolbox = apt 판(slam_build:=apt)')]


# 2026-09-30 F1 이어 그리기: map_file:=<경로(확장자 없이)> 면 저장된 포즈 그래프(.posegraph/.data)를 불러와
#   map_start_pose(출발 테이프 자세, 기본 0,0,0)에서 매핑을 이어 간다. 비우면(기본) 지금처럼 새 지도.
#   저장은 /slam_toolbox/serialize_map(포즈 그래프) + /slam_toolbox/save_map(격자 pgm/yaml) — jobs/job684_map_save.sh.
#   근거·절차: Docs/debug_log/2026-09-30/SUMMARY.md §4
# 2026-10-01 F1-4: slam_mode:=mapping(기본) | localization. localization 은 지도(포즈 그래프)를 고정하고 위치만 추정한다
#   (localization_slam_toolbox_node, mode: localization — 실행 중 스캔은 짧은 버퍼로만 두고 저장 지도는 바꾸지 않음).
#   운용(주행) 중 지도를 이어 그리다 루프 클로저 오정합으로 깨지는 문제(09-30 §13~16)를 피하려는 후보. AMCL 대안은
#   rover_navigation/launch/localization.launch.py. 비교 근거: Docs/debug_log/2026-10-01/SUMMARY.md §7
def _make_slam(context):
    config = os.path.join(get_package_share_directory('rover_bringup'), 'config', 'slam.yaml')
    params = [config]
    mode = LaunchConfiguration('slam_mode').perform(context).strip()
    if mode not in ('mapping', 'localization'):
        raise RuntimeError('slam_mode 는 mapping|localization: %s' % mode)
    mf = LaunchConfiguration('map_file').perform(context).strip()
    if mode == 'localization' and not mf:
        raise RuntimeError('slam_mode:=localization 은 map_file 이 필요합니다')
    if mf:
        x, y, th = (float(v) for v in LaunchConfiguration('map_start_pose').perform(context).split(','))
        params.append({'map_file_name': mf, 'map_start_pose': [x, y, th], 'map_start_at_dock': False})
        msg = '[slam.launch] %s: %s 에서 시작 자세 (%.3f, %.3f, %.3f)' % (
            '위치 추정(지도 고정)' if mode == 'localization' else '이어 그리기', mf, x, y, th)
    else:
        msg = '[slam.launch] 새 지도'
    exe = 'async_slam_toolbox_node'
    if mode == 'localization':
        # 2026-10-01 §9: 위치 추정 모드 전용 부하 설정. 매핑용 노드 간격(0.05 m·0.03 rad)을 그대로 쓰면 주행 중 스캔 처리가 밀려
        #   map→odom 이 최대 1 s 멈추고(0.2 s 넘게 늦은 시간 14.5 %, CPU 134 %) 컨트롤러가 로봇 자세를 map 으로 못 바꿔 목표 중단(f2a1).
        #   09-30 bag 재생 A/B: 0.30 m·0.15 rad + 지도 다시 그리기 10 s → 0.19 %·최대 0.40 s·CPU 22 %(t3m).
        #   지도 다시 그리기는 위치 추정 모드에서 지도가 사실상 안 바뀌므로 간격을 늘려도 잃는 것이 적다.
        # 2026-10-01 §8.5: transform_timeout 0.2 → 0.5. slam_toolbox 는 map→odom 스탬프를 '마지막 스캔 시각 + transform_timeout' 으로
        #   미래에 찍는다(slam_toolbox_common.cpp publishTransformLoop). 처리가 밀려 이 미래 여유가 다 소진되면(f2a2 실주행 최대 0.57 s 밀림)
        #   컨트롤러가 로봇 자세를 map 으로 바꾸지 못해 follow_path 가 중단된다(f2a2 3 회, 밀림이 0.04 ms 만 넘어도 실패 — 대기 없이 즉시 실패).
        #   0.5 s 면 관측 최대 밀림을 거의 덮는다. 대가: 0.5 s 안의 보정 변화가 늦게 반영될 수 있으나 map→odom 은 느리게 변하는 보정값이라 영향 작음(추정).
        params.append({'mode': 'localization', 'minimum_travel_distance': 0.30,
                       'minimum_travel_heading': 0.15, 'map_update_interval': 10.0,
                       'transform_timeout': 0.5})
        exe = 'localization_slam_toolbox_node'
    return [LogInfo(msg=msg), Node(
        package='slam_toolbox', executable=exe,
        name='slam_toolbox', output='screen',
        parameters=params,
    )]


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument('slam_build', default_value='fork', description='slam_toolbox 빌드: fork | apt'),
        DeclareLaunchArgument('map_file', default_value='', description='이어 그릴 포즈 그래프 경로(확장자 없이). 비우면 새 지도'),
        DeclareLaunchArgument('map_start_pose', default_value='0.0,0.0,0.0', description='이어 그리기 시작 자세 x,y,yaw (map 기준, 출발 테이프)'),
        DeclareLaunchArgument('slam_mode', default_value='mapping', description='mapping(기본) | localization(지도 고정, map_file 필요)'),
        SetEnvironmentVariable('FASTRTPS_DEFAULT_PROFILES_FILE', _FASTDDS_XML),
        OpaqueFunction(function=_select_build),
        OpaqueFunction(function=_make_slam),
    ])
