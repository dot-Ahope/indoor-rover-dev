#!/usr/bin/env python3
"""회피 주행 계측판 (2026-09-09) — job92 의 여유 측정이 틀렸던 것을 고친다.

job92 의 오류: '최소 여유' 를 실시간 깊이 포인트클라우드에서 쟀다. 로버가 상자 옆을 지나기
시작하면 상자가 카메라 화각을 벗어나 그 값이 멀리 있는 다른 물체로 바뀐다. job124 에서
28.0cm 로 보고했지만 CSV 로 기하 계산한 실제 최근접은 0.0cm(접촉)였다.

여기서는 세 가지를 동시에 기록해 '경로가 안쪽으로 옮겨갔는지' vs '코스트맵이 상자를 잃었는지'
를 가른다:
  1) clear_geo : 출발 시 map 에 고정한 상자 사각형 ↔ 차체 사각형의 실제 거리 (카메라 무관)
  2) plan_clear: 그 순간의 /plan 이 상자에서 얼마나 떨어져 있는가 (차체 반폭 제외한 여유)
  3) lc_box / gc_box : 로컬·전역 코스트맵이 상자 자리에 아직 비용을 갖고 있는가
사용: python3 job125_avoid3.py [D=1.80] [timeout=90] [csv이름=job125]
"""
import math, sys, time, csv, rclpy, tf2_ros
import numpy as np
from rclpy.node import Node
from rclpy.action import ActionClient
from nav2_msgs.action import NavigateToPose
from nav_msgs.msg import Path, OccupancyGrid
from sensor_msgs.msg import PointCloud2
from geometry_msgs.msg import PoseStamped, Twist
from rclpy.qos import qos_profile_sensor_data, QoSProfile, DurabilityPolicy, ReliabilityPolicy

D = float(sys.argv[1]) if len(sys.argv) > 1 else 1.80
TMO = float(sys.argv[2]) if len(sys.argv) > 2 else 90.0
NAME = sys.argv[3] if len(sys.argv) > 3 else 'job125'
HL, HW = 0.25, 0.165          # 차체 반길이 / 반폭 (실제 외곽, 패딩 제외)
BOX_W, BOX_D = 0.18, 0.11     # 사용자 실측: 폭(가로) 0.18, 정면(세로) 0.11

rclpy.init(); n = Node('avoid125')
buf = tf2_ros.Buffer(); tl = tf2_ros.TransformListener(buf, n)
S = {'cmd': (0.0, 0.0), 'path': []}
qos_tl = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL,
                    reliability=ReliabilityPolicy.RELIABLE)
n.create_subscription(Twist, '/cmd_vel', lambda m: S.__setitem__('cmd', (m.linear.x, m.angular.z)), 10)
n.create_subscription(Path, '/plan',
                      lambda m: S.__setitem__('path', [(p.pose.position.x, p.pose.position.y) for p in m.poses]), 10)
n.create_subscription(PointCloud2, '/camera/camera/depth/color/points',
                      lambda m: S.__setitem__('pc', m), qos_profile_sensor_data)
n.create_subscription(OccupancyGrid, '/local_costmap/costmap', lambda m: S.__setitem__('lc', m), qos_tl)
n.create_subscription(OccupancyGrid, '/global_costmap/costmap', lambda m: S.__setitem__('gc', m), qos_tl)


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
    xyz = np.stack([raw[:, off[k]:off[k]+4].copy().view(np.float32).ravel() for k in ('x', 'y', 'z')], axis=1)
    xyz = xyz[np.isfinite(xyz).all(axis=1)]
    return xyz @ Rq(tr.rotation).T + np.array([tr.translation.x, tr.translation.y, tr.translation.z])


def pose(frame='map'):
    try:
        t = buf.lookup_transform(frame, 'base_link', rclpy.time.Time()).transform
        q = t.rotation
        return (t.translation.x, t.translation.y, math.atan2(2*(q.w*q.z), 1-2*q.z*q.z))
    except Exception:
        return None


def dist_pt_to_footprint(px, py):
    """차체 좌표계 점 → 차체 외곽 사각형까지 거리 (내부면 0)."""
    return math.hypot(max(abs(px)-HL, 0.0), max(abs(py)-HW, 0.0))


# ── 1) TF/센서 준비 ─────────────────────────────────────────────
t0 = time.time()
while time.time()-t0 < 20 and (pose() is None or 'pc' not in S or 'lc' not in S):
    rclpy.spin_once(n, timeout_sec=0.1)
p0 = pose()
if p0 is None:
    print("TF 실패"); raise SystemExit(1)

# ── 2) 상자 map 좌표 확정 ───────────────────────────────────────
# 2026-09-09: 카메라 정적 TF 를 명시적으로 기다린다. pose() 는 map→base_link 만 요구하므로
#   그것이 성립해도 camera_depth_optical_frame 은 아직 버퍼에 없을 수 있다(다른 발행자).
#   foxglove_bridge 가 CPU 를 많이 쓰는 상태에서 /tf_static 전달이 늦어 검출이 실패했다(job136).
tw = time.time()
while time.time()-tw < 20:
    try:
        buf.lookup_transform('base_link', 'camera_depth_optical_frame', rclpy.time.Time())
        break
    except Exception:
        rclpy.spin_once(n, timeout_sec=0.1)
else:
    print("카메라 TF 대기 실패 (base_link ← camera_depth_optical_frame)"); raise SystemExit(1)

BOX = None
for attempt in range(60):
    P = cloud('base_link')
    if P is not None:
        sel = P[(P[:, 2] > 0.05) & (P[:, 2] < 0.30) & (P[:, 0] > 0.5) & (P[:, 0] < 1.5) & (np.abs(P[:, 1]) < 0.5)]
        if len(sel) >= 40:
            # 폭은 백분위수로 (min/max 는 이상점에 끌려간다 — 09-08 오진 사례)
            cy = float(np.median(sel[:, 1]))
            fx = float(np.percentile(sel[:, 0], 5))     # 전면 x
            c, s = math.cos(p0[2]), math.sin(p0[2])
            # base → map
            corners = []
            for bx, by in ((fx, cy-BOX_W/2), (fx, cy+BOX_W/2),
                           (fx+BOX_D, cy+BOX_W/2), (fx+BOX_D, cy-BOX_W/2)):
                corners.append((p0[0] + bx*c - by*s, p0[1] + bx*s + by*c))
            BOX = dict(corners=corners, n=len(sel), base=(fx, cy))
            break
    rclpy.spin_once(n, timeout_sec=0.2)
if BOX is None:
    P = cloud('base_link')
    nn = 0 if P is None else int(((P[:, 2] > 0.05) & (P[:, 2] < 0.30) &
                                  (P[:, 0] > 0.5) & (P[:, 0] < 1.5) & (np.abs(P[:, 1]) < 0.5)).sum())
    print("상자 검출 실패 — 조건 통과 점 %d개(40 필요). 전방 0.5~1.5m 에 낮은 물체가 보여야 합니다"
          % nn); raise SystemExit(1)

# 상자 둘레를 촘촘히 샘플링 (사각형 ↔ 사각형 거리를 점-사각형 거리의 최소로 근사)
CS = BOX['corners']
peri = []
for i in range(4):
    ax, ay = CS[i]; bx, by = CS[(i+1) % 4]
    for k in range(21):
        u = k/20.0
        peri.append((ax + u*(bx-ax), ay + u*(by-ay)))
PERI = np.array(peri)
bx_min, bx_max = PERI[:, 0].min(), PERI[:, 0].max()
by_min, by_max = PERI[:, 1].min(), PERI[:, 1].max()
BOXC = (float(PERI[:, 0].mean()), float(PERI[:, 1].mean()))
print("상자 확정: map x %.3f~%.3f, y %+.3f~%+.3f (검출점 %d, base 전면 %.2f)"
      % (bx_min, bx_max, by_min, by_max, BOX['n'], BOX['base'][0]))


def clear_geo(px, py, yaw):
    """차체 외곽 ↔ 상자 외곽 최소 거리 (m). 0 이면 접촉."""
    c, s = math.cos(-yaw), math.sin(-yaw)
    dx = PERI[:, 0] - px; dy = PERI[:, 1] - py
    rx = dx*c - dy*s; ry = dx*s + dy*c            # 차체 좌표계
    ex = np.maximum(np.abs(rx) - HL, 0.0)
    ey = np.maximum(np.abs(ry) - HW, 0.0)
    return float(np.min(np.hypot(ex, ey)))


def plan_clear():
    """현재 /plan 이 상자에서 떨어진 최소 거리 − 차체 반폭. 음수면 계획 자체가 접촉 경로."""
    P = S['path']
    if len(P) < 2:
        return float('nan'), float('nan')
    A = np.array(P)
    # 경로점 ↔ 상자 둘레 최소 거리
    d = np.min(np.hypot(A[:, None, 0] - PERI[None, :, 0], A[:, None, 1] - PERI[None, :, 1]))
    # 상자 x 근처에서의 경로 횡좌표 (출발 자세 기준)
    c, s = math.cos(p0[2]), math.sin(p0[2])
    fx = (A[:, 0]-p0[0])*c + (A[:, 1]-p0[1])*s
    fy = -(A[:, 0]-p0[0])*s + (A[:, 1]-p0[1])*c
    bxf = (BOXC[0]-p0[0])*c + (BOXC[1]-p0[1])*s
    k = int(np.argmin(np.abs(fx - bxf)))
    return d - HW, float(fy[k])


def cost_at(key, frame, x, y):
    """map 좌표 (x,y) 의 코스트맵 비용. 로컬은 odom 프레임이라 변환한다."""
    if key not in S:
        return -1
    g = S[key]; i = g.info
    if frame != 'map':
        try:
            t = buf.lookup_transform(frame, 'map', rclpy.time.Time()).transform
            q = t.rotation; th = math.atan2(2*(q.w*q.z), 1-2*q.z*q.z)
            c, s = math.cos(th), math.sin(th)
            x, y = t.translation.x + x*c - y*s, t.translation.y + x*s + y*c
        except Exception:
            return -1
    cx = int((x-i.origin.position.x)/i.resolution); cy = int((y-i.origin.position.y)/i.resolution)
    if not (0 <= cx < i.width and 0 <= cy < i.height):
        return -1
    return g.data[cy*i.width+cx]


# ── 3) 목표 전송 ────────────────────────────────────────────────
ch, sh = math.cos(p0[2]), math.sin(p0[2])
GX, GY = p0[0] + D*ch, p0[1] + D*sh
print("출발 (%.2f,%.2f) hd=%.1f° → 목표 (%.2f,%.2f)" % (p0[0], p0[1], math.degrees(p0[2]), GX, GY), flush=True)
ac = ActionClient(n, NavigateToPose, 'navigate_to_pose'); ac.wait_for_server(timeout_sec=10.0)
g = NavigateToPose.Goal(); g.pose = PoseStamped(); g.pose.header.frame_id = 'map'
g.pose.header.stamp = n.get_clock().now().to_msg()
g.pose.pose.position.x, g.pose.pose.position.y = GX, GY
g.pose.pose.orientation.z, g.pose.pose.orientation.w = math.sin(p0[2]/2), math.cos(p0[2]/2)
fut = ac.send_goal_async(g); rclpy.spin_until_future_complete(n, fut, timeout_sec=30.0)
gh = fut.result()
if gh is None or not gh.accepted:
    print("목표 거부"); raise SystemExit(1)

rf = gh.get_result_async(); t1 = time.time(); rows = []; nxt = t1; log = t1
print("  t   전진   횡변위 | 실여유 계획여유 계획횡 | lc_box gc_box | v_cmd  w_cmd", flush=True)
while not rf.done() and time.time()-t1 < TMO:
    rclpy.spin_once(n, timeout_sec=0.01)
    now = time.time(); p = pose()
    if p is None or now < nxt:
        continue
    nxt += 0.1
    rel = (p[0]-p0[0], p[1]-p0[1])
    fwd = rel[0]*ch + rel[1]*sh; lat = -rel[0]*sh + rel[1]*ch
    cg = clear_geo(p[0], p[1], p[2])
    pc, pfy = plan_clear()
    lb = cost_at('lc', 'odom', *BOXC); gb = cost_at('gc', 'map', *BOXC)
    rows.append((now-t1, fwd, lat, cg, pc, pfy, lb, gb, S['cmd'][0], S['cmd'][1]))
    if now >= log:
        log += 1.0
        print("%5.1f %+.3f %+.3f | %6.3f %8.3f %+6.3f | %5d %5d | %+.3f %+.3f"
              % (now-t1, fwd, lat, cg, pc, pfy, lb, gb, S['cmd'][0], S['cmd'][1]), flush=True)

if not rf.done():
    gh.cancel_goal_async(); rclpy.spin_once(n, timeout_sec=2.0); res = 'TIMEOUT'
else:
    res = {4: 'SUCCEEDED', 5: 'CANCELED', 6: 'ABORTED'}.get(rf.result().status, str(rf.result().status))

with open('/tmp/%s.csv' % NAME, 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['t', 'fwd', 'lat', 'clear_geo', 'plan_clear', 'plan_lat_at_box', 'lc_box', 'gc_box', 'v', 'w'])
    w.writerows(rows)

cg = [r[3] for r in rows]
pcl = [r[4] for r in rows if not math.isnan(r[4])]
k = int(np.argmin(cg))
straight = [r for r in rows if abs(r[8]) > 0.03]
flips = sum(1 for i in range(1, len(straight))
            if straight[i][9]*straight[i-1][9] < 0 and abs(straight[i][9]) > 0.01 and abs(straight[i-1][9]) > 0.01)
dist = sum(math.hypot(rows[i][1]-rows[i-1][1], rows[i][2]-rows[i-1][2]) for i in range(1, len(rows)))
print("")
print("결과 %s  소요 %.1fs  주행 %.2fm  샘플 %d" % (res, rows[-1][0], dist, len(rows)))
print("  ① 실제 최근접(차체↔상자 기하): %.1f cm @ t=%.1fs 전진 %.2f 횡 %+.3f   ← 0 이면 접촉"
      % (min(cg)*100, rows[k][0], rows[k][1], rows[k][2]))
if pcl:
    j = int(np.argmin(pcl))
    print("  ② 계획의 최소 여유: %.1f cm (최근접 시점 %.1f cm)   ← 음수면 계획 자체가 접촉 경로"
          % (min(pcl)*100, rows[k][4]*100))
print("  ③ 상자 자리 비용 — 로컬 최소/최근접시 %d/%d, 전역 최소/최근접시 %d/%d  ← 0 이면 기억 소실"
      % (min(r[6] for r in rows), rows[k][6], min(r[7] for r in rows), rows[k][7]))
# ④ 경로 좌우 전환 — 양안정성 지표. 상자 x 위치에서의 계획 횡좌표 부호가 바뀐 횟수.
#    |y| < 0.05 인 애매한 구간은 노이즈로 보고 직전 부호를 유지한다.
side, flips_plan, first = 0, 0, None
for r in rows:
    v = r[5]
    if math.isnan(v) or abs(v) < 0.05:
        continue
    sgn = 1 if v > 0 else -1
    if first is None:
        first = sgn
    elif sgn != side:
        flips_plan += 1
    side = sgn
neg = sum(1 for r in rows if not math.isnan(r[4]) and r[4] < 0)
print("  ④ 경로 좌우 전환 %d회 (최초 선택 %s), 계획이 접촉 경로였던 샘플 %d/%d (%.0f%%)"
      % (flips_plan, {1: '좌', -1: '우', None: '?'}[first], neg, len(rows), 100.0*neg/max(len(rows), 1)))
print("  조향: 직진 중 |ω| 평균 %.3f 최대 %.3f rad/s, 부호반전 %d회 = %.1f회/m"
      % (sum(abs(r[9]) for r in straight)/max(len(straight), 1),
         max((abs(r[9]) for r in straight), default=0), flips, flips/max(dist, 0.01)))
rclpy.shutdown()
