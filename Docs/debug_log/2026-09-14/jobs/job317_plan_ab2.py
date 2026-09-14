#!/usr/bin/env python3
"""계획기 A/B — NavFn(GridBased) vs Smac Hybrid-A*(SmacHybrid), 정지 상태, 주행 없음 (2026-09-14, NVBLOX 계획서 §5-3).

  같은 시작 pose(use_start)·같은 목표에서 두 계획을 받아, 중앙 상자 코스의 실패 지점(상자 앞왼쪽 모서리) 기준으로 비교한다:
    - 모서리 통과 시 heading: 경로가 x = BX−0.30 ~ BX 를 지날 때의 접선 각(작을수록 앞우 모서리가 덜 쓸린다)
    - 차선 변경 시작 위치: 횡이 +0.10 을 처음 넘는 x (일찍 시작할수록 완만)
    - 경로의 상자 셀·좌측 셀 최소거리(전역 코스트맵 LETHAL), 접선 급변 최대, 길이
  인자: START_X START_Y START_YAW_deg GOAL_FWD GOAL_LAT BX BY   (모두 map/시작프레임 기준: 시작 pose 로 목표·상자를 변환)
"""
import sys, math, time
import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from rclpy.qos import QoSProfile, DurabilityPolicy, ReliabilityPolicy
from nav2_msgs.action import ComputePathToPose
from nav_msgs.msg import OccupancyGrid
from geometry_msgs.msg import PoseStamped

SX, SY, SYAW = float(sys.argv[1]), float(sys.argv[2]), math.radians(float(sys.argv[3]))
GF, GL = float(sys.argv[4]), float(sys.argv[5])
BX, BY = float(sys.argv[6]), float(sys.argv[7])
PLANNERS = sys.argv[8].split(',') if len(sys.argv) > 8 else ['GridBased', 'SmacHybrid']
rclpy.init(); n = Node('planab317')
G = {}
n.create_subscription(OccupancyGrid, '/global_costmap/costmap', lambda m: G.__setitem__('g', m),
                      QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL, reliability=ReliabilityPolicy.RELIABLE))
ac = ActionClient(n, ComputePathToPose, '/compute_path_to_pose')
if not ac.wait_for_server(timeout_sec=10.0):
    print('planner 액션 없음'); sys.exit(1)
t0 = time.time()
while time.time() - t0 < 15 and 'g' not in G:
    rclpy.spin_once(n, timeout_sec=0.1)


def to_map(f, l):
    return (SX + f * math.cos(SYAW) - l * math.sin(SYAW), SY + f * math.sin(SYAW) + l * math.cos(SYAW))


def to_start(x, y):
    dx, dy = x - SX, y - SY
    return (dx * math.cos(SYAW) + dy * math.sin(SYAW), -dx * math.sin(SYAW) + dy * math.cos(SYAW))


gx, gy = to_map(GF, GL)
print('시작 map (%.3f, %.3f, %+.1f°) → 목표 전진 %.2f 횡 %+.2f = map (%.3f, %.3f); 상자 전면 %.2f 중심 %+.2f' % (SX, SY, math.degrees(SYAW), GF, GL, gx, gy, BX, BY))
g = G.get('g')
lethal = np.zeros((0, 2))
if g:
    d = np.array(g.data, dtype=np.int16).reshape(g.info.height, g.info.width); jj, ii = np.where(d >= 100)
    X = g.info.origin.position.x + (ii + 0.5) * g.info.resolution; Y = g.info.origin.position.y + (jj + 0.5) * g.info.resolution
    lethal = np.array([to_start(x, y) for x, y in zip(X, Y)]) if len(X) else lethal
    box = lethal[(lethal[:, 0] > BX - 0.15) & (lethal[:, 0] < BX + 0.45) & (lethal[:, 1] > BY - 0.4) & (lethal[:, 1] < BY + 0.4)]
    left = lethal[(lethal[:, 0] > 0.0) & (lethal[:, 0] < BX + 0.6) & (lethal[:, 1] > BY + 0.4) & (lethal[:, 1] < BY + 1.2)]
    print('전역 LETHAL: 상자 %d셀 (y %+.2f~%+.2f), 좌측 %d셀 (y 최소 %+.2f)' % (len(box), box[:, 1].min() if len(box) else 0, box[:, 1].max() if len(box) else 0, len(left), left[:, 1].min() if len(left) else 0))
else:
    box = left = lethal
    print('전역 코스트맵 없음')


def plan(pid):
    goal = ComputePathToPose.Goal()
    goal.goal = PoseStamped(); goal.goal.header.frame_id = 'map'; goal.goal.pose.position.x = gx; goal.goal.pose.position.y = gy
    goal.goal.pose.orientation.z = math.sin(SYAW / 2); goal.goal.pose.orientation.w = math.cos(SYAW / 2)
    goal.start = PoseStamped(); goal.start.header.frame_id = 'map'; goal.start.pose.position.x = SX; goal.start.pose.position.y = SY
    goal.start.pose.orientation.z = math.sin(SYAW / 2); goal.start.pose.orientation.w = math.cos(SYAW / 2)
    goal.use_start = True; goal.planner_id = pid
    t1 = time.time()
    fut = ac.send_goal_async(goal)
    while not fut.done():
        rclpy.spin_once(n, timeout_sec=0.05)
    gh = fut.result()
    if not gh or not gh.accepted:
        print('  [%s] 거부' % pid); return None
    rf = gh.get_result_async()
    while not rf.done() and time.time() - t1 < 20:
        rclpy.spin_once(n, timeout_sec=0.05)
    res = rf.result()
    dt = time.time() - t1
    if not res or res.status != 4 or not res.result.path.poses:
        print('  [%s] 실패 status %s (%.2f s)' % (pid, res.status if res else '-', dt)); return None
    P = np.array([to_start(p.pose.position.x, p.pose.position.y) for p in res.result.path.poses])
    L = float(np.sum(np.hypot(np.diff(P[:, 0]), np.diff(P[:, 1]))))
    # 접선
    tang = np.degrees(np.arctan2(np.gradient(P[:, 1]), np.gradient(P[:, 0])))
    seg = (P[:, 0] >= BX - 0.30) & (P[:, 0] <= BX)
    hd_corner = float(np.max(np.abs(tang[seg]))) if seg.any() else float('nan')
    pass_lat = float(np.median(P[(P[:, 0] >= BX) & (P[:, 0] <= BX + 0.3), 1])) if ((P[:, 0] >= BX) & (P[:, 0] <= BX + 0.3)).any() else float('nan')
    first = P[np.argmax(P[:, 1] > 0.10), 0] if (P[:, 1] > 0.10).any() else float('nan')
    hd_max = float(np.max(np.abs(tang[(P[:, 0] > 0.2) & (P[:, 0] < BX + 0.3)]))) if ((P[:, 0] > 0.2) & (P[:, 0] < BX + 0.3)).any() else float('nan')
    dt3 = np.abs(np.diff(tang)); dt3 = np.minimum(dt3, 360 - dt3); kink = float(dt3.max()) if len(dt3) else 0
    dbox = float(min(np.hypot(box[:, 0] - p[0], box[:, 1] - p[1]).min() for p in P)) if len(box) else float('nan')
    dleft = float(min(np.hypot(left[:, 0] - p[0], left[:, 1] - p[1]).min() for p in P)) if len(left) else float('nan')
    print('  [%-10s] %.2f s, %d점, 길이 %.2f m | 차선변경 시작 x %.2f | 모서리 구간(x %.2f~%.2f) |접선| 최대 %.1f° | 진입 전체 |접선| 최대 %.1f° | 상자 옆 횡 %+.3f | 상자 셀 최소 %.3f, 좌측 셀 최소 %.3f | 접선 급변 %.1f°/점'
          % (pid, dt, len(P), L, first, BX - 0.30, BX, hd_corner, hd_max, pass_lat, dbox, dleft, kink))
    rows = []
    for f in np.arange(0.2, BX + 0.4, 0.2):
        m = (P[:, 0] >= f) & (P[:, 0] < f + 0.2)
        if m.any():
            rows.append('%.1f:%+.2f/%+.0f°' % (f, np.median(P[m, 1]), np.median(tang[m])))
    print('      전진:횡/접선  ' + '  '.join(rows))
    return P


for pid in PLANNERS:
    plan(pid)
