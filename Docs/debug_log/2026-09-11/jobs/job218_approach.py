#!/usr/bin/env python3
"""접근 실험 — 로컬 코스트맵이 상자를 버리는 지점을 통제된 조건에서 잡는다 (2026-09-11).

  배경 (job216, SUMMARY 11.2): 깊이점이 끊긴 뒤 **1.3초 만에** 로컬이 상자를 통째로
  버렸다. decay_model:-1(영속)이므로 감쇠가 아니고, 같은 STVL 설정의 전역은 끝까지
  유지했으므로 로컬 고유 요인이다. 후보는 update_footprint_enabled / 절두체 clearing /
  rolling_window 셋.

  왜 회피 주행(job194)이 아니라 이 실험인가:
    회피 주행은 회전·우회가 섞여 조건이 여러 개 동시에 바뀐다. 여기서는 **직선으로 천천히
    접근만** 해서 바뀌는 변수를 '거리' 하나로 줄인다. 한 번에 60초, 파라미터 1개씩 바꿔
    반복하면 원인이 분리된다.

  절차: 상자를 정면에 두고 v=0.04 m/s 로 전진 -> lc_box 가 무너지는 순간의 거리를 기록
        -> 즉시 정지 -> 같은 거리만큼 후진 복귀(다음 시행을 같은 조건에서).
  안전: clear_geo(차체-상자 기하) < STOP_CLEAR 이면 무조건 정지. 타임아웃 정지.

  사용: python3 job218_approach.py [이름=job218] [정지여유m=0.12] [타임아웃s=70]
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

NAME = sys.argv[1] if len(sys.argv) > 1 else 'job218'
STOP_CLEAR = float(sys.argv[2]) if len(sys.argv) > 2 else 0.12
TMO = float(sys.argv[3]) if len(sys.argv) > 3 else 70.0
V = 0.04
HL, HW = 0.25, 0.165          # 차체 반길이 / 반폭
CAMX = 0.232                  # base_link -> camera_link x (URDF)
BOX_W, BOX_D = 0.18, 0.11     # 상자 폭 / 깊이 (사용자 실측)

rclpy.init()
n = Node('appr218')
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
    """y 축 1D 클러스터링 — 2026-09-10 수정. 벽과 상자를 가른다."""
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
    """상자를 base_link 에서 찾아 map 중심좌표와 관측 점수를 낸다."""
    P = cloud('base_link')
    if P is None:
        return None
    sel = P[(P[:, 2] > 0.05) & (P[:, 2] < 0.30) & (P[:, 0] > 0.2) & (P[:, 0] < 1.5)
            & (np.abs(P[:, 1]) < 0.5)]
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
    return dict(map=(pnow[0] + cx*co - cy*si, pnow[1] + cx*si + cy*co),
                base=(fx, cy), n=len(c))


def cost_at(g, x, y):
    if g is None:
        return -1
    i = int((x - g.info.origin.position.x) / g.info.resolution)
    j = int((y - g.info.origin.position.y) / g.info.resolution)
    if 0 <= i < g.info.width and 0 <= j < g.info.height:
        return g.data[j * g.info.width + i]
    return -1


def cost_max(g, mx, my, r=0.10):
    """상자 중심 +-r 안의 최대 비용. 한 셀이 아니라 영역을 봐야 재고정 오차에 덜 민감하다."""
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

# 카메라 정적 TF 대기 — /tf_static 전달이 늦으면 cloud() 가 통째로 None 이 된다
tw = time.time()
while time.time() - tw < 20:
    try:
        buf.lookup_transform('base_link', 'camera_depth_optical_frame', rclpy.time.Time())
        break
    except Exception:
        rclpy.spin_once(n, timeout_sec=0.1)
else:
    print('카메라 TF 없음 (base_link <- camera_depth_optical_frame)')
    stop()
    raise SystemExit(1)

B = detect(p0)
if B is None:
    print('상자를 못 찾음 — 정면 0.2~1.5m 에 낮은 물체(z 0.05~0.30)가 보여야 한다')
    stop()
    raise SystemExit(2)
print('상자 map (%.3f, %.3f)  base_link 전면 x=%.3f y=%+.3f  %d점'
      % (B['map'][0], B['map'][1], B['base'][0], B['base'][1], B['n']))
print('출발 로버 map (%.3f, %.3f) hd=%.1f deg' % (p0[0], p0[1], math.degrees(p0[2])))
print()
print('   t   전진   clear_geo  cam~box   깊이점   lc   gc')

BM = B['map']
rows = []
collapse = None
t0 = time.time()
nxt = 0.0
cmd = Twist()
cmd.linear.x = V
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
    if d is not None and math.hypot(d['map'][0] - BM[0], d['map'][1] - BM[1]) < 0.30:
        BM = d['map']          # 보일 때만 재고정
    npts = d['n'] if d is not None else 0
    co, si = math.cos(p[2]), math.sin(p[2])
    rx = (BM[0] - p[0]) * co + (BM[1] - p[1]) * si
    ry = -(BM[0] - p[0]) * si + (BM[1] - p[1]) * co
    cg = math.hypot(max(abs(rx) - HL - BOX_D/2, 0.0), max(abs(ry) - HW - BOX_W/2, 0.0))
    cam = math.hypot(rx - CAMX, ry) - BOX_D/2
    lc = cost_max(S.get('lc'), BM[0], BM[1])
    gc = cost_max(S.get('gc'), BM[0], BM[1])
    fwd = math.hypot(p[0] - p0[0], p[1] - p0[1])
    rows.append((el, fwd, cg, cam, npts, lc, gc))
    print('%6.1f  %.3f   %6.3f   %6.3f   %6d  %3d  %3d' % (el, fwd, cg, cam, npts, lc, gc))
    if collapse is None and lc < 50 and len(rows) > 4:
        collapse = (el, fwd, cg, cam, npts)
        print('  ** 로컬 붕괴 — cam~box %.3f m, clear_geo %.3f m, 그때 깊이점 %d'
              % (cam, cg, npts))
    if cg < STOP_CLEAR:
        print('  안전 정지 (clear_geo %.3f < %.2f)' % (cg, STOP_CLEAR))
        break
    if collapse is not None and el - collapse[0] > 4.0:
        print('  붕괴 후 4초 관측 완료 — 정지')
        break
stop()

print()
print('=== 요약 ===')
if collapse:
    print('  로컬 붕괴: t=%.1f  전진 %.3f m  clear_geo %.3f m  cam~box %.3f m  그때 깊이점 %d'
          % collapse)
else:
    print('  로컬 붕괴 없음 (끝까지 유지)')
seen = [r for r in rows if r[4] > 0]
if seen:
    r = seen[-1]
    print('  깊이 마지막 관측: t=%.1f  cam~box %.3f m  %d점' % (r[0], r[3], r[4]))
    if collapse:
        print('  소실 -> 붕괴 간격: %.1f 초 (%.3f m 전진)'
              % (collapse[0] - r[0], collapse[1] - r[1]))
gcmin = min((r[6] for r in rows), default=-1)
print('  전역 최소 비용: %d  (로컬과 대비)' % gcmin)
back = rows[-1][1] if rows else 0.0
print()
print('  복귀: python3 /tmp/job218_back.py %.3f' % back)
with open('/tmp/%s.csv' % NAME, 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['t', 'fwd', 'clear_geo', 'cam_box', 'pts', 'lc', 'gc'])
    w.writerows(rows)
print('  CSV: /tmp/%s.csv (%d행)' % (NAME, len(rows)))
