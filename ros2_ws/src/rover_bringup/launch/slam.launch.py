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
def _make_slam(context):
    config = os.path.join(get_package_share_directory('rover_bringup'), 'config', 'slam.yaml')
    params = [config]
    mf = LaunchConfiguration('map_file').perform(context).strip()
    if mf:
        x, y, th = (float(v) for v in LaunchConfiguration('map_start_pose').perform(context).split(','))
        params.append({'map_file_name': mf, 'map_start_pose': [x, y, th], 'map_start_at_dock': False})
        msg = '[slam.launch] 이어 그리기: %s 에서 시작 자세 (%.3f, %.3f, %.3f)' % (mf, x, y, th)
    else:
        msg = '[slam.launch] 새 지도'
    return [LogInfo(msg=msg), Node(
        package='slam_toolbox', executable='async_slam_toolbox_node',
        name='slam_toolbox', output='screen',
        parameters=params,
    )]


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument('slam_build', default_value='fork', description='slam_toolbox 빌드: fork | apt'),
        DeclareLaunchArgument('map_file', default_value='', description='이어 그릴 포즈 그래프 경로(확장자 없이). 비우면 새 지도'),
        DeclareLaunchArgument('map_start_pose', default_value='0.0,0.0,0.0', description='이어 그리기 시작 자세 x,y,yaw (map 기준, 출발 테이프)'),
        SetEnvironmentVariable('FASTRTPS_DEFAULT_PROFILES_FILE', _FASTDDS_XML),
        OpaqueFunction(function=_select_build),
        OpaqueFunction(function=_make_slam),
    ])
