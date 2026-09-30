# foxglove_bridge — PC Foxglove Studio에서 ws://<jetson-ip>:8765 접속 (RViz 대체)
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

# ── 화이트리스트 ────────────────────────────────────────────────────────────
# bridge가 서빙할 토픽을 정규식 full-match로 제한한다.
#   근거(2026-09-01): 과부하된 bridge가 /tf를 늦게 전달 → Foxglove에서 로봇이 4초마다 점프.
#   근거(2026-09-09): bridge가 상시 CPU 88~95%(≈1코어)로 최대 소비자였고, 같은 시기
#     ekf_node 가 "Failed to meet update rate! Took 0.14s"를 반복했다. 비용은 코어 수가 아니라
#     **메시지 건수 × 직렬화**에서 나오므로, 고주파 토픽을 빼는 것이 가장 직접적인 절감이다.
#
# LEAN(기본) — 주행 진단에 실제로 보는 것만. 합산 약 60 msg/s.
LEAN = [
    # 좌표계 — 없으면 아무것도 못 본다
    '/tf', '/tf_static', '/robot_description',
    # 지도·스캔
    '/map', '/map_metadata',
    '/scan',                       # 10Hz. /scan_raw 는 디스큐 전 원본이라 중복 → 제외
    # 상태
    '/odometry/filtered',          # 30Hz. /wheel_odom(25Hz)은 이것의 입력이라 중복 → FULL 로
    '/rover/status', '/battery', '/rover/stuck',
    '/cmd_vel',
    # 코스트맵·경로 (회피 진단의 핵심)
    #   always_send_full_costmap: true 이므로 *_updates 토픽은 **발행되지 않는다** → 제외
    '/local_costmap/costmap', '/global_costmap/costmap',
    '/plan', '/local_plan',
]

# FULL — 센서 원본까지 보고 싶을 때. `viz:=full`
#   ⚠ /imu/data 는 **200Hz** 다(D455f 자이로). LEAN 에서 뺀 가장 큰 이유가 이것이다.
FULL = LEAN + [
    '/imu/data', '/imu/data_raw', '/imu/mag',
    '/wheel_odom', '/scan_raw', '/joy',
]

# CAM — 카메라 영상까지. 대역·CPU 부담이 크므로 필요할 때만. `viz:=cam`
CAM = FULL + [
    '/camera/camera/color/image_raw', '/camera/camera/color/camera_info',
    '/camera/camera/depth/image_rect_raw',
    '/camera/camera/depth/color/points',
]

# MAP — 매핑하며 지도·로버 위치만 볼 때. `viz:=map` (2026-09-30, Docs/debug_log/2026-09-30/SUMMARY.md §5)
#   근거: 매핑 중 Foxglove 연결(LEAN) 시 EKF 주기 미달 12 회/30 s·EKF CPU 49 % → 끊으면 0 회·12 %, 부하 10.1 → 5.5.
#   EKF 가 밀려 odom TF 가 늦으면 SLAM 이 스캔을 버려(106 회) 지도 위 로버가 멈췄다 점프했다.
#   코스트맵 전체 격자(매 갱신 통째로)·odometry·경로를 빼고, 파라미터·서비스 기능도 끈다(아래 CAPS).
MAP = ['/tf', '/tf_static', '/robot_description', '/map', '/map_metadata', '/scan']

SETS = {'lean': LEAN, 'full': FULL, 'cam': CAM, 'map': MAP}
# 브리지 기능: parameters 는 앱이 전 노드 파라미터를 가져오며 서비스 요청을 뿌린다(§5 로그의 조회 실패 연속).
#   MAP 은 보기 전용이라 최소(clientPublish 만 — 빈 목록은 ROS 파라미터 타입 문제로 피함; 조종은 패드).
CAPS = {'map': ['clientPublish']}
_CAPS_DEFAULT = ['clientPublish', 'parameters', 'services']


def _make(context, *args, **kwargs):
    level = LaunchConfiguration('viz').perform(context)
    wl = SETS.get(level, LEAN)
    return [Node(
        package='foxglove_bridge', executable='foxglove_bridge', name='foxglove_bridge',
        output='screen',
        parameters=[{
            'port': 8765,
            'address': '0.0.0.0',
            'topic_whitelist': wl,
            # 2026-09-09 부하 억제 (foxglove_bridge 3.2.4 — 파라미터 존재 확인함)
            'num_threads': 2,          # 기본 0 = 코어 수(6). 상한을 둬 다른 노드의 몫을 남긴다
            # 밀리면 큐에 쌓지 말고 버린다 (시각화는 최신 것만 의미 있음).
            # 2026-09-30 §12: map 세트는 10 — /tf 한 토픽에 EKF(odom→base 30 Hz)·SLAM(map→odom)·기타가 섞여 들어와 깊이 1 이면
            #   다른 발행자의 /tf 에 밀려 로버 변환이 버려짐 → Foxglove 에서 스캔만 돌고 로버는 멈췄다 점프(Jetson 쪽 TF 는 정상, j712).
            'max_qos_depth': 10 if level == 'map' else 1,
            'send_buffer_limit': 2000000,
            'use_compression': False,  # 압축은 CPU 를 더 쓴다. 유선/근거리 Wi-Fi 라 불필요
            # 기본 capabilities 에는 connectionGraph·parametersSubscribe·assets 가 포함되어
            # 그래프/파라미터를 주기적으로 폴링한다. 시각화에는 불필요하므로 뺀다.
            # 되돌리려면 이 줄만 지우면 기본값으로 돌아간다.
            'capabilities': CAPS.get(level, _CAPS_DEFAULT),
        }],
    )]


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument(
            'viz', default_value='lean',
            description="foxglove 로 내보낼 토픽 범위: lean(기본) | full(센서 원본) | cam(영상 포함) | map(매핑 보기 전용, 가벼움)"),
        OpaqueFunction(function=_make),
    ])
