#!/usr/bin/env python3
"""회전 실험 — 로컬 코스트맵이 상자를 버리는 '방위'를 잡는다 (2026-09-11).

  왜 접근이 아니라 회전인가 (trial0 결과):
    정면 접근(v=0.04)에서는 cam~box 0.15m 까지 가도 로컬이 상자를 끝까지 유지했다.
    job216 에서 붕괴한 순간을 궤적으로 재구성하면 로버 진행방향 +27.2 도, 상자 맵 방위
    -19.6 도 -> **로버 기준 상자 방위 -46.8 도**. D455 수평 화각 87도(반각 43.5도)를
    막 벗어난 지점이다. 즉 방아쇠는 거리가 아니라 **방위**로 보인다.
    거리를 고정하고 방위만 바꾸면 화각 경계 통과 시점을 정확히 집을 수 있다.

  절차: 제자리 회전(v=0)으로 상자를 화각 밖으로 보내고, 매 0.25초
        상자 방위(로버 기준) / 깊이점 / lc / gc 를 기록. 붕괴하면 그 방위를 남기고,
        지정 각도까지 돌면 반대로 같은 각도만큼 되돌아온다.

  사용: python3 job220_rotate.py [이름=job220] [목표각도deg=75] [방향 1|-1=1]
        방향 1 = 반시계(CCW, 상자가 오른쪽으로 밀려남), -1 = 시계
"""
import sys
import time
import math
import csv
import numpy as np
import rclpy
import tf2_ros
from rclpy.node import Node
from sensor_msgs.msg import PointCloud2
from nav_msgs.msg import OccupancyGrid
from geometry_msgs.msg import Twist
from rclpy.qos import qos_profile_sensor_data, QoSProfile, DurabilityPolicy, ReliabilityPolicy

NAME = sys.argv[1] if len(sys.argv) > 1 else 'job220'
GOAL_DEG = float(sys.argv[2]) if len(sys.argv) > 2 else 75.0
DIRN = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
W = 0.20 * (1.0 if DIRN >= 0 else -1.0)
HFOV_HALF = math.degrees(1.518) / 2.0   # nav2_params 의 horizontal_fov_angle
BOX_W, BOX_D = 0.18, 0.11
CAMX = 0.232

rclpy.init()
n = Node('rot220')
buf = tf2_ros.Buffer()
tl = tf2_ros.TransformListener(buf, n)
S = {}
qos_tl = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL,
                    reliability=ReliabilityPolicy.RELIABLE)
n.create_subscription(PointCloud2, '/camera/camera/depth/color/points',
                      lambda m: S.__setitem__('pc', m), qos_profile_sensor_data)
n.create_subscription(OccupancyGrid, '/local_costmap/costmap',
                      lambda m: S.__setitem__('lc', m), qos_tl)
n.create_subscription(OccupancyGrid, '/global_costmap/costmap',
                      lambda m: S.__setitem__('gc', m), qos_tl)
pub = n.create_publisher(Twist, '/cmd_vel', 10)


def Rq(q):
    w, x, y, z = q.w, q.x, q.y, q.z
    return np.array([[1-2*(y*y+z*z), 2*(x*y-z*w), 2*(x*z+y*w)],
                     [2*(x*y+z*w), 1-2*(x*x+z*z), 2*(y*z-x*w)],
                     [2*(x*z-y*w), 2*(y*z+x*w), 1-2*(x*x+y*y)]])


def cloud(frame):
    if 'pc' not in S:
        return None
    m = S['pc']
    try:
        tr = buf.lookup_transform(frame, m.header.frame_id, rclpy.time.Time()).transform
    except Exception:
        return None
    off = {f.name: f.offset for f in m.fields}
    raw = np.frombuffer(m.data, dtype=np.uint8).reshape(-1, m.point_step)
    xyz = np.stack([raw[:, off[k]:off[k]+4].copy().view(np.float32).ravel()
                    for k in ('x', 'y', 'z')], axis=1)
    xyz = xyz[np.isfinite(xyz).all(axis=1)]
    return xyz @ Rq(tr.rotation).T + np.array(
        [tr.translation.x, tr.translation.y, tr.translation.z])


def clusters_y(sel, gap=0.08, minpts=25):
    if len(sel) == 0:
        return []
    o = sel[np.argsort(sel[:, 1])]
    out, cur = [], [o[0]]
    for p in o[1:]:
        if p[1] - cur[-1][1] > gap:
            if len(cur) >= minpts:
                out.append(np.array(cur))
            cur = [p]
        else:
            cur.append(p)
    if len(cur) >= minpts:
        out.append(np.array(cur))
    return out


def pose():
    try:
        t = buf.lookup_transform('map', 'base_link', rclpy.time.Time()).transform
        q = t.rotation
        return (t.translation.x, t.translation.y, math.atan2(2*(q.w*q.z), 1-2*q.z*q.z))
    except Exception:
        return None


def detect(pnow):
    P = cloud('base_link')
    if P is None:
        return None
    sel = P[(P[:, 2] > 0.05) & (P[:, 2] < 0.30) & (P[:, 0] > 0.2) & (P[:, 0] < 1.5)
            & (np.abs(P[:, 1]) < 0.8)]
    low = [(abs(float(np.median(c[:, 1]))), c) for c in clusters_y(sel)
           if float(np.median(c[:, 2])) < 0.20]
    if not low:
        return None
    low.sort(key=lambda t: t[0])
    c = low[0][1]
    fx = float(np.percentile(c[:, 0], 5))
    cy = float(np.median(c[:, 1]))
    cx = fx + BOX_D / 2
    co, si = math.cos(pnow[2]), math.sin(pnow[2])
    return dict(map=(pnow[0] + cx*co - cy*si, pnow[1] + cx*si + cy*co), n=len(c))


def cost_at(g, x, y):
    if g is None:
        return -1
    i = int((x - g.info.origin.position.x) / g.info.resolution)
    j = int((y - g.info.origin.position.y) / g.info.resolution)
    if 0 <= i < g.info.width and 0 <= j < g.info.height:
        return g.data[j * g.info.width + i]
    return -1


def cost_max(g, mx, my, r=0.10):
    best = -1
    d = 0.05
    k = int(r / d)
    for a in range(-k, k + 1):
        for b in range(-k, k + 1):
            v = cost_at(g, mx + a*d, my + b*d)
            if v > best:
                best = v
    return best


def stop():
    t = Twist()
    for _ in range(5):
        pub.publish(t)
        time.sleep(0.05)


t0 = time.time()
while time.time() - t0 < 20 and (pose() is None or 'pc' not in S
                                 or 'lc' not in S or 'gc' not in S):
    rclpy.spin_once(n, timeout_sec=0.1)
p0 = pose()
if p0 is None or 'lc' not in S:
    print('TF/코스트맵 준비 실패')
    stop()
    raise SystemExit(1)
tw = time.time()
while time.time() - tw < 20:
    try:
        buf.lookup_transform('base_link', 'camera_depth_optical_frame', rclpy.time.Time())
        break
    except Exception:
        rclpy.spin_once(n, timeout_sec=0.1)
else:
    print('카메라 TF 없음')
    stop()
    raise SystemExit(1)

B = detect(p0)
if B is None:
    print('상자를 못 찾음')
    stop()
    raise SystemExit(2)
BM = B['map']
print('상자 map (%.3f, %.3f)  %d점' % (BM[0], BM[1], B['n']))
print('출발 로버 map (%.3f, %.3f) hd=%.1f deg' % (p0[0], p0[1], math.degrees(p0[2])))
print('카메라 수평 화각 반각 = %.1f deg (이 값을 넘으면 화각 밖)' % HFOV_HALF)
print()
print('   t   회전각   상자방위   거리    깊이점   lc   gc   화각')

rows = []
collapse = None
lost = None
t0 = time.time()
nxt = 0.0
cmd = Twist()
cmd.angular.z = W
TMO = abs(GOAL_DEG) / abs(math.degrees(W)) + 20.0
while time.time() - t0 < TMO:
    rclpy.spin_once(n, timeout_sec=0.02)
    pub.publish(cmd)
    el = time.time() - t0
    if el < nxt:
        continue
    nxt += 0.25
    p = pose()
    if p is None:
        continue
    d = detect(p)
    if d is not None and math.hypot(d['map'][0] - BM[0], d['map'][1] - BM[1]) < 0.25:
        BM = d['map']
    npts = d['n'] if d is not None else 0
    co, si = math.cos(p[2]), math.sin(p[2])
    rx = (BM[0] - p[0]) * co + (BM[1] - p[1]) * si
    ry = -(BM[0] - p[0]) * si + (BM[1] - p[1]) * co
    # 카메라 원점 기준 방위
    bear = math.degrees(math.atan2(ry, rx - CAMX))
    dist = math.hypot(rx - CAMX, ry)
    rot = math.degrees((p[2] - p0[2] + math.pi) % (2*math.pi) - math.pi)
    lc = cost_max(S.get('lc'), BM[0], BM[1])
    gc = cost_max(S.get('gc'), BM[0], BM[1])
    inside = 'IN ' if abs(bear) <= HFOV_HALF else 'OUT'
    rows.append((el, rot, bear, dist, npts, lc, gc, inside.strip()))
    print('%6.1f  %+7.1f  %+8.1f  %6.3f  %6d  %3d  %3d   %s'
          % (el, rot, bear, dist, npts, lc, gc, inside))
    if lost is None and npts == 0 and len(rows) > 3:
        lost = (el, rot, bear, dist)
        print('  -- 깊이 소실: 방위 %+.1f deg, 거리 %.3f m' % (bear, dist))
    if npts > 0:
        lost = None
    if collapse is None and lc < 50 and len(rows) > 3:
        collapse = (el, rot, bear, dist, npts)
        print('  ** 로컬 붕괴: 상자 방위 %+.1f deg (화각 반각 %.1f), 거리 %.3f m, 깊이점 %d'
              % (bear, HFOV_HALF, dist, npts))
    if abs(rot) >= abs(GOAL_DEG):
        print('  목표 회전 %.0f deg 도달' % GOAL_DEG)
        break
    if collapse is not None and el - collapse[0] > 5.0:
        print('  붕괴 후 5초 관측 완료')
        break
stop()

print()
print('=== 요약 ===')
if collapse:
    print('  로컬 붕괴: 회전 %+.1f deg 에서, 상자 방위 %+.1f deg, 거리 %.3f m, 깊이점 %d'
          % (collapse[1], collapse[2], collapse[3], collapse[4]))
    print('  화각 반각 %.1f deg 대비: %s'
          % (HFOV_HALF, '화각 밖' if abs(collapse[2]) > HFOV_HALF else '화각 안'))
else:
    print('  로컬 붕괴 없음')
seen = [r for r in rows if r[4] > 0]
if seen:
    r = seen[-1]
    print('  깊이 마지막 관측: 방위 %+.1f deg, 거리 %.3f m, %d점' % (r[2], r[3], r[4]))
print('  전역 최소: %d' % min((r[6] for r in rows), default=-1))
back = rows[-1][1] if rows else 0.0
print()
print('  복귀: python3 /tmp/job220_rotate.py back %.1f %d' % (abs(back), -1 if back > 0 else 1))
with open('/tmp/%s.csv' % NAME, 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['t', 'rot_deg', 'bearing_deg', 'dist', 'pts', 'lc', 'gc', 'fov'])
    w.writerows(rows)
print('  CSV: /tmp/%s.csv (%d행)' % (NAME, len(rows)))
