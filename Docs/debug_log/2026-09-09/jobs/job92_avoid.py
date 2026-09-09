#!/usr/bin/env python3
"""회피 주행 검증 (2026-09-09) — inflation 0.40/패딩 0.02 배포 후 첫 실주행.
  사용: python3 job92_avoid.py [D=1.80] [timeout=90] [csv이름=job92]
계획이 아니라 '실제로 얼마나 붙었는가' 를 본다:
  - 차체 외곽(반길이 0.25, 반폭 0.165 + 패딩 0.02)에서 깊이점까지의 최소 여유 (실시간)
  - 시작 시 검출한 상자 map 좌표까지의 거리 (드리프트 영향 받지만 참고)
  - 경로 횡오차, 직진 중 omega 부호반전 (조향 진동)
'최소 여유' 가 0 에 닿으면 접촉이다."""
import math, sys, time, csv, rclpy, tf2_ros
import numpy as np
from rclpy.node import Node
from rclpy.action import ActionClient
from nav2_msgs.action import NavigateToPose
from nav_msgs.msg import Path
from sensor_msgs.msg import PointCloud2
from geometry_msgs.msg import PoseStamped, Twist
from rclpy.qos import qos_profile_sensor_data

D = float(sys.argv[1]) if len(sys.argv) > 1 else 1.80
TMO = float(sys.argv[2]) if len(sys.argv) > 2 else 90.0
NAME = sys.argv[3] if len(sys.argv) > 3 else 'job92'
HALF_L, HALF_W = 0.25, 0.185      # 패딩 포함 외곽

rclpy.init(); n = Node('avoid92')
buf = tf2_ros.Buffer(); tl = tf2_ros.TransformListener(buf, n)
S = {'cmd': (0.0, 0.0), 'path': []}
n.create_subscription(Twist, '/cmd_vel', lambda m: S.__setitem__('cmd', (m.linear.x, m.angular.z)), 10)
n.create_subscription(Path, '/plan', lambda m: S.__setitem__('path', [(p.pose.position.x, p.pose.position.y) for p in m.poses]), 10)
n.create_subscription(PointCloud2, '/camera/camera/depth/color/points', lambda m: S.__setitem__('pc', m), qos_profile_sensor_data)


def Rq(q):
    w, x, y, z = q.w, q.x, q.y, q.z
    return np.array([[1-2*(y*y+z*z), 2*(x*y-z*w), 2*(x*z+y*w)],
                     [2*(x*y+z*w), 1-2*(x*x+z*z), 2*(y*z-x*w)],
                     [2*(x*z-y*w), 2*(y*z+x*w), 1-2*(x*x+y*y)]])


def cloud_base():
    if 'pc' not in S:
        return None
    m = S['pc']
    try:
        tr = buf.lookup_transform('base_link', m.header.frame_id, rclpy.time.Time()).transform
    except Exception:
        return None
    off = {f.name: f.offset for f in m.fields}
    step = m.point_step
    raw = np.frombuffer(m.data, dtype=np.uint8).reshape(-1, step)
    xyz = np.stack([raw[:, off[k]:off[k]+4].copy().view(np.float32).ravel() for k in ('x', 'y', 'z')], axis=1)
    xyz = xyz[np.isfinite(xyz).all(axis=1)]
    return xyz @ Rq(tr.rotation).T + np.array([tr.translation.x, tr.translation.y, tr.translation.z])


def clearance():
    """차체 외곽 사각형에서 장애물 깊이점까지 최소 거리(m). 점 없으면 nan."""
    P = cloud_base()
    if P is None:
        return float('nan'), 0
    sel = P[(P[:, 2] > 0.03) & (P[:, 2] < 0.35) & (P[:, 0] > -0.1) & (P[:, 0] < 1.5) & (np.abs(P[:, 1]) < 0.9)]
    if len(sel) == 0:
        return float('nan'), 0
    dx = np.maximum(np.abs(sel[:, 0]) - HALF_L, 0.0)
    dy = np.maximum(np.abs(sel[:, 1]) - HALF_W, 0.0)
    return float(np.min(np.hypot(dx, dy))), len(sel)


def pose():
    try:
        t = buf.lookup_transform('map', 'base_link', rclpy.time.Time()).transform
        q = t.rotation
        return (t.translation.x, t.translation.y, math.atan2(2*(q.w*q.z), 1-2*q.z*q.z))
    except Exception:
        return None


def lat_err(x, y):
    P = S['path']
    if len(P) < 2:
        return float('nan')
    best = 1e9
    for i in range(len(P)-1):
        ax, ay = P[i]
        bx, by = P[i+1]
        ddx, ddy = bx-ax, by-ay
        L2 = ddx*ddx + ddy*ddy
        tt = 0.0 if L2 < 1e-9 else max(0.0, min(1.0, ((x-ax)*ddx + (y-ay)*ddy)/L2))
        best = min(best, math.hypot(x-(ax+tt*ddx), y-(ay+tt*ddy)))
    return best


t0 = time.time()
while time.time()-t0 < 12 and (pose() is None or 'pc' not in S):
    rclpy.spin_once(n, timeout_sec=0.1)
p0 = pose()
if p0 is None:
    print("TF 실패")
    raise SystemExit(1)

# 상자 map 좌표 고정
P = cloud_base()
BX = BY = None
if P is not None:
    sel = P[(P[:, 2] > 0.05) & (P[:, 2] < 0.30) & (P[:, 0] > 0.5) & (P[:, 0] < 1.4) & (np.abs(P[:, 1]) < 0.45)]
    if len(sel) > 30:
        bx, by = float(np.median(sel[:, 0])), float(np.median(sel[:, 1]))
        c, s = math.cos(p0[2]), math.sin(p0[2])
        BX, BY = p0[0] + bx*c - by*s, p0[1] + bx*s + by*c
        print("상자 검출: base (%.2f,%+.2f) 점 %d -> map (%.2f,%+.2f)" % (bx, by, len(sel), BX, BY))
ch, sh = math.cos(p0[2]), math.sin(p0[2])
GX, GY = p0[0] + D*ch, p0[1] + D*sh
print("출발 (%.2f,%.2f) hd=%.1f deg -> 목표 (%.2f,%.2f)" % (p0[0], p0[1], math.degrees(p0[2]), GX, GY), flush=True)

ac = ActionClient(n, NavigateToPose, 'navigate_to_pose')
ac.wait_for_server(timeout_sec=10.0)
g = NavigateToPose.Goal()
g.pose = PoseStamped()
g.pose.header.frame_id = 'map'
g.pose.header.stamp = n.get_clock().now().to_msg()
g.pose.pose.position.x, g.pose.pose.position.y = GX, GY
g.pose.pose.orientation.z, g.pose.pose.orientation.w = math.sin(p0[2]/2), math.cos(p0[2]/2)
fut = ac.send_goal_async(g)
rclpy.spin_until_future_complete(n, fut, timeout_sec=30.0)
gh = fut.result()
if gh is None or not gh.accepted:
    print("목표 거부")
    raise SystemExit(1)

rf = gh.get_result_async()
t1 = time.time()
rows = []
nxt = t1
log = t1
print("  t   전진   횡변위  최소여유  상자거리  v_cmd  w_cmd  횡오차", flush=True)
while not rf.done() and time.time()-t1 < TMO:
    rclpy.spin_once(n, timeout_sec=0.01)
    now = time.time()
    p = pose()
    if p is None:
        continue
    if now >= nxt:
        nxt += 0.1
        cl, npt = clearance()
        rel = (p[0]-p0[0], p[1]-p0[1])
        fwd = rel[0]*ch + rel[1]*sh
        lat = -rel[0]*sh + rel[1]*ch
        bd = math.hypot(BX-p[0], BY-p[1]) if BX is not None else float('nan')
        rows.append((now-t1, fwd, lat, cl, bd, S['cmd'][0], S['cmd'][1], lat_err(p[0], p[1]), npt))
        if now >= log:
            log += 1.0
            print("%5.1f %+.3f %+.3f   %6.3f   %6.3f  %+.3f %+.3f  %.3f"
                  % (now-t1, fwd, lat, cl, bd, S['cmd'][0], S['cmd'][1], rows[-1][7]), flush=True)
if not rf.done():
    gh.cancel_goal_async()
    rclpy.spin_once(n, timeout_sec=2.0)
    res = 'TIMEOUT'
else:
    res = {4: 'SUCCEEDED', 5: 'CANCELED', 6: 'ABORTED'}.get(rf.result().status, str(rf.result().status))

with open('/tmp/%s.csv' % NAME, 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['t', 'fwd', 'lat', 'clear', 'boxdist', 'v', 'w', 'lat_err', 'npts'])
    w.writerows(rows)

p1 = pose()
dist = sum(math.hypot(rows[i][1]-rows[i-1][1], rows[i][2]-rows[i-1][2]) for i in range(1, len(rows)))
cl = [r[3] for r in rows if not math.isnan(r[3])]
lats = [r[2] for r in rows]
le = [r[7] for r in rows if not math.isnan(r[7])]
straight = [r for r in rows if abs(r[5]) > 0.03]
flips = sum(1 for i in range(1, len(straight))
            if straight[i][6]*straight[i-1][6] < 0 and abs(straight[i][6]) > 0.01 and abs(straight[i-1][6]) > 0.01)
print("")
print("결과 %s  소요 %.1fs  주행 %.2fm  샘플 %d" % (res, rows[-1][0], dist, len(rows)))
if cl:
    k = int(np.argmin([r[3] if not math.isnan(r[3]) else 9 for r in rows]))
    print("  최소 여유(차체 외곽->깊이점): %.1fcm  @ t=%.1fs 전진 %.2fm  (0 이면 접촉)"
          % (min(cl)*100, rows[k][0], rows[k][1]))
else:
    print("  여유 측정 실패")
print("  최대 좌측 변위 %+.1fcm / 최대 우측 %+.1fcm" % (max(lats)*100, min(lats)*100))
if le:
    print("  경로 횡오차 RMS %.1fcm, 최대 %.1fcm" % (math.sqrt(sum(x*x for x in le)/len(le))*100, max(le)*100))
print("  직진 중 omega 부호반전 %d회 = %.1f회/m" % (flips, flips/max(dist, 0.01)))
print("  최종 위치오차 %.1fcm" % (math.hypot(p1[0]-GX, p1[1]-GY)*100))
rclpy.shutdown()
