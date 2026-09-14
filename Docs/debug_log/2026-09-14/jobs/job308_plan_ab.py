#!/usr/bin/env python3
"""정지 상태 계획 A/B — inflation_radius 가 '상자 옆 틈' 에서 계획을 어디에 놓는가 (2026-09-11). 로버는 움직이지 않는다.

  v5 정체: 상자(우) 와 좌측 물체 사이 0.6~0.75 m 틈에서 전역 계획이 상자 쪽(+0.45, 상자 inflation 0.35 의 비용 0 경계)
  에 붙고, 좌측 물체 선단 셀이 나타나자 계획이 상자 쪽으로 더 꺾여(접선 −21°→−40°) 로버 앞우 모서리가 상자
  셀 3~7 cm 까지 갔다. inflation 을 키우면 양쪽 비용 경사가 겹쳐 최소가 틈 중앙에 생긴다는 가설을
  ComputePathToPose 로만(주행 없이) 검증한다.
    A: 현재값(전역 0.35 / 3.0)   B: 0.55 / 2.0   → 끝나면 A 복원 + 읽어서 확인
  지표: 계획의 차체좌표 횡 위치(전방 띠별), 계획~상자 LETHAL 최소거리, 계획~좌측 물체 LETHAL 최소거리, 접선 변화 최대.
"""
import sys, math, time, subprocess
import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from rclpy.qos import QoSProfile, DurabilityPolicy, ReliabilityPolicy
from nav2_msgs.action import ComputePathToPose
from nav_msgs.msg import OccupancyGrid
from geometry_msgs.msg import PoseStamped
import tf2_ros

GOAL_FWD = float(sys.argv[1]) if len(sys.argv) > 1 else 2.1
GOAL_LAT = float(sys.argv[2]) if len(sys.argv) > 2 else 0.0
B_R, B_S = (sys.argv[3], sys.argv[4]) if len(sys.argv) > 4 else ('0.55', '2.0')
rclpy.init()
n = Node('planab308')
buf = tf2_ros.Buffer(); tl = tf2_ros.TransformListener(buf, n)
G = {}
qos_tl = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL, reliability=ReliabilityPolicy.RELIABLE)
n.create_subscription(OccupancyGrid, '/global_costmap/costmap', lambda m: G.__setitem__('g', m), qos_tl)
ac = ActionClient(n, ComputePathToPose, '/compute_path_to_pose')
if not ac.wait_for_server(timeout_sec=10.0):
    print('planner 액션 없음'); sys.exit(1)


def sh(cmd):
    return subprocess.run('source /opt/ros/humble/setup.bash; ' + cmd, shell=True, capture_output=True, text=True, executable='/bin/bash').stdout.strip()


def get_params():
    r = sh('timeout 6 ros2 param get /global_costmap/global_costmap inflation_layer.inflation_radius').split('is:')[-1].strip()
    s = sh('timeout 6 ros2 param get /global_costmap/global_costmap inflation_layer.cost_scaling_factor').split('is:')[-1].strip()
    return r, s


def set_params(r, s):
    sh('timeout 8 ros2 param set /global_costmap/global_costmap inflation_layer.inflation_radius %s' % r)
    sh('timeout 8 ros2 param set /global_costmap/global_costmap inflation_layer.cost_scaling_factor %s' % s)
    return get_params()


def pose():
    t = buf.lookup_transform('map', 'base_link', rclpy.time.Time(), timeout=rclpy.duration.Duration(seconds=5.0)).transform
    q = t.rotation
    return (t.translation.x, t.translation.y, math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z)))


t0 = time.time()
# TF 리스너가 map->odom 을 받을 때까지 기다린다 (조회를 바로 하면 'map does not exist' — 09-14 실사고)
while time.time() - t0 < 30 and ('g' not in G or not buf.can_transform('map', 'base_link', rclpy.time.Time())):
    rclpy.spin_once(n, timeout_sec=0.1)
if not buf.can_transform('map', 'base_link', rclpy.time.Time()):
    print('map->base_link TF 없음 (SLAM 미동작?)'); sys.exit(1)
px, py, pyaw = pose()
gx = px + GOAL_FWD * math.cos(pyaw) - GOAL_LAT * math.sin(pyaw); gy = py + GOAL_FWD * math.sin(pyaw) + GOAL_LAT * math.cos(pyaw)
print('로버 map (%.3f, %.3f) yaw %+.1f° → 목표 전방 %.2f 횡 %+.2f = map (%.3f, %.3f)' % (px, py, math.degrees(pyaw), GOAL_FWD, GOAL_LAT, gx, gy))


def body(x, y):
    dx, dy = x - px, y - py
    return (dx * math.cos(pyaw) + dy * math.sin(pyaw), -dx * math.sin(pyaw) + dy * math.cos(pyaw))


def lethal_sets():
    g = G['g']; res = g.info.resolution; ox, oy = g.info.origin.position.x, g.info.origin.position.y
    d = np.array(g.data, dtype=np.int16).reshape(g.info.height, g.info.width)
    jj, ii = np.where(d >= 100)
    X = ox + (ii + 0.5) * res; Y = oy + (jj + 0.5) * res
    B = np.array([body(x, y) for x, y in zip(X, Y)]) if len(X) else np.zeros((0, 2))
    box = B[(B[:, 0] > 1.2) & (B[:, 0] < 1.9) & (B[:, 1] > -0.7) & (B[:, 1] < -0.15)]
    obj = B[(B[:, 0] > 0.9) & (B[:, 0] < 1.7) & (B[:, 1] > 0.25) & (B[:, 1] < 1.1)]
    return box, obj, d, g


def cost_at(g, d, x, y):
    i = int((x - g.info.origin.position.x) / g.info.resolution); j = int((y - g.info.origin.position.y) / g.info.resolution)
    return int(d[j, i]) if 0 <= i < g.info.width and 0 <= j < g.info.height else -1


def plan_once(label):
    goal = ComputePathToPose.Goal()
    goal.goal = PoseStamped(); goal.goal.header.frame_id = 'map'; goal.goal.pose.position.x = gx; goal.goal.pose.position.y = gy
    goal.goal.pose.orientation.z = math.sin(pyaw / 2); goal.goal.pose.orientation.w = math.cos(pyaw / 2)
    goal.use_start = False; goal.planner_id = 'GridBased'
    fut = ac.send_goal_async(goal)
    while not fut.done():
        rclpy.spin_once(n, timeout_sec=0.05)
    gh = fut.result()
    if not gh or not gh.accepted:
        print('  [%s] 계획 요청 거부' % label); return None
    rf = gh.get_result_async(); t1 = time.time()
    while not rf.done() and time.time() - t1 < 15:
        rclpy.spin_once(n, timeout_sec=0.05)
    res = rf.result()
    if not res or res.status != 4:
        print('  [%s] 계획 실패 status %s' % (label, res.status if res else '-')); return None
    pts = [(p.pose.position.x, p.pose.position.y) for p in res.result.path.poses]
    B = np.array([body(x, y) for x, y in pts])
    box, obj, d, g = lethal_sets()
    for _ in range(5):
        rclpy.spin_once(n, timeout_sec=0.05)
    print('  [%s] 경로 %d점, 상자 LETHAL %d셀 (전방 %.2f~%.2f 횡 %+.2f~%+.2f), 좌측물체 LETHAL %d셀 (전방 %.2f~%.2f 횡 %+.2f~%+.2f)'
          % (label, len(pts), len(box), box[:, 0].min() if len(box) else 0, box[:, 0].max() if len(box) else 0, box[:, 1].min() if len(box) else 0, box[:, 1].max() if len(box) else 0,
             len(obj), obj[:, 0].min() if len(obj) else 0, obj[:, 0].max() if len(obj) else 0, obj[:, 1].min() if len(obj) else 0, obj[:, 1].max() if len(obj) else 0))
    out = {}
    print('     전방 띠     계획 횡(중앙값)   상자까지   좌측물체까지   경로점 비용(최대)')
    for lo in np.arange(0.4, GOAL_FWD, 0.2):
        m = (B[:, 0] >= lo) & (B[:, 0] < lo + 0.2)
        if not m.any():
            continue
        seg = B[m]; lat = float(np.median(seg[:, 1]))
        dbox = min(np.hypot(box[:, 0] - p[0], box[:, 1] - p[1]).min() for p in seg) if len(box) else float('nan')
        dobj = min(np.hypot(obj[:, 0] - p[0], obj[:, 1] - p[1]).min() for p in seg) if len(obj) else float('nan')
        cmax = max(cost_at(g, d, x, y) for (x, y), bb in zip(pts, B) if lo <= bb[0] < lo + 0.2)
        out[round(lo, 1)] = (lat, dbox, dobj)
        print('     %.1f~%.1f     %+.3f          %.2f       %.2f          %3d' % (lo, lo + 0.2, lat, dbox, dobj, cmax))
    # 접선 변화
    ang = [math.atan2(B[i + 3][1] - B[i][1], B[i + 3][0] - B[i][0]) for i in range(0, len(B) - 3)]
    dmax = max(abs(math.degrees((ang[i + 1] - ang[i] + math.pi) % (2 * math.pi) - math.pi)) for i in range(len(ang) - 1)) if len(ang) > 1 else 0
    # 최소 여유 (전체 경로에서 상자/물체까지)
    dbox_all = min(np.hypot(box[:, 0] - p[0], box[:, 1] - p[1]).min() for p in B) if len(box) else float('nan')
    dobj_all = min(np.hypot(obj[:, 0] - p[0], obj[:, 1] - p[1]).min() for p in B) if len(obj) else float('nan')
    print('     경로 전체: 상자 LETHAL 최소 %.2f m, 좌측물체 최소 %.2f m, 접선 급변 최대 %.0f°/3점  (내접반경 0.195 → 두 값 모두 ≥0.195 여야 통과)' % (dbox_all, dobj_all, dmax))
    return out


a = get_params(); print('A 현재: inflation_radius %s, cost_scaling %s' % a)
ra = plan_once('A %s/%s' % a)
b = set_params(B_R, B_S); print('B 적용 → readback: inflation_radius %s, cost_scaling %s' % b)
t1 = time.time()
while time.time() - t1 < 4.0:
    rclpy.spin_once(n, timeout_sec=0.1)
rb = plan_once('B %s/%s' % b)
c = set_params(a[0], a[1]); print('A 복원 → readback: inflation_radius %s, cost_scaling %s' % c)
if ra and rb:
    print()
    print('=== A→B 변화 (전방 띠, 계획 횡 / 상자 여유 / 물체 여유) ===')
    for k in sorted(set(ra) & set(rb)):
        print('  %.1f: 횡 %+.3f→%+.3f   상자 %.2f→%.2f   물체 %.2f→%.2f' % (k, ra[k][0], rb[k][0], ra[k][1], rb[k][1], ra[k][2], rb[k][2]))
