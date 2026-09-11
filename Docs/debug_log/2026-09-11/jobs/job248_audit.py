#!/usr/bin/env python3
"""구성 전면 점검 — 물리 공간 vs 코스트맵 vs 컨트롤러 판정 기준 (2026-09-11).

  사용자 지적: "차가 그렇게 크지 않은데 환각이 너무 심하다."
  → 로버 0.5x0.33 m, 통로 1.2~1.8 m. 그런데 나는 "0.7~0.9 m 필요, 통과 불가" 라고 했다.
    숫자가 맞지 않는다. 도구의 판정 기준부터 의심한다.

  A) 물리 통로: 라이다(2D) + 깊이(z 0.06~0.40) 장애물 점을 상자 x 구간에서 y 로 정렬해
     실제 빈 틈을 잰다. 차체 0.33 / 패딩 포함 0.43 과 비교한다.
  B) 코스트맵 감사: 로컬 코스트맵의 LETHAL(100) 셀마다 가장 가까운 센서 점까지 거리.
     센서 점이 8cm 안에 없는 LETHAL = 근거 없는 마킹(과마킹).
  C) 컨트롤러 기준: RPP 는 footprint 둘레 최대비용 >= LETHAL(254=발행 100) 일 때만 충돌.
     inscribed(253=99)는 '중심이 여기면 충돌' 이라 이미 반경이 반영된 값 — footprint 를
     투영하면서 99 를 쓰면 반경을 두 번 센다(오늘 job228/job233 의 오류).
     둘 다 계산해 차이를 보인다.
  로버는 움직이지 않는다.
"""
import math
import time
import numpy as np
import rclpy
import tf2_ros
from rclpy.node import Node
from nav_msgs.msg import OccupancyGrid
from sensor_msgs.msg import LaserScan, PointCloud2
from rclpy.qos import qos_profile_sensor_data, QoSProfile, DurabilityPolicy, ReliabilityPolicy

HL, HW, PAD = 0.25, 0.165, 0.05
BOX_W, BOX_D = 0.18, 0.11
LETHAL_PUB, INSCRIBED_PUB = 100, 99

rclpy.init()
n = Node('audit248')
buf = tf2_ros.Buffer()
tl = tf2_ros.TransformListener(buf, n)
S = {}
qos_tl = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL,
                    reliability=ReliabilityPolicy.RELIABLE)
n.create_subscription(OccupancyGrid, '/local_costmap/costmap', lambda m: S.__setitem__('lc', m), qos_tl)
n.create_subscription(OccupancyGrid, '/global_costmap/costmap', lambda m: S.__setitem__('gc', m), qos_tl)
n.create_subscription(LaserScan, '/scan', lambda m: S.__setitem__('sc', m), qos_profile_sensor_data)
n.create_subscription(PointCloud2, '/camera/camera/depth/color/points',
                      lambda m: S.__setitem__('pc', m), qos_profile_sensor_data)


def Rq(q):
    w, x, y, z = q.w, q.x, q.y, q.z
    return np.array([[1-2*(y*y+z*z), 2*(x*y-z*w), 2*(x*z+y*w)],
                     [2*(x*y+z*w), 1-2*(x*x+z*z), 2*(y*z-x*w)],
                     [2*(x*z-y*w), 2*(y*z+x*w), 1-2*(x*x+y*y)]])


def tfm(a, b):
    t = buf.lookup_transform(a, b, rclpy.time.Time()).transform
    return Rq(t.rotation), np.array([t.translation.x, t.translation.y, t.translation.z])


def pose():
    try:
        t = buf.lookup_transform('map', 'base_link', rclpy.time.Time()).transform
        q = t.rotation
        return (t.translation.x, t.translation.y,
                math.atan2(2*(q.w*q.z + q.x*q.y), 1 - 2*(q.y*q.y + q.z*q.z)))
    except Exception:
        return None


t0 = time.time()
while time.time() - t0 < 25 and (pose() is None or len(S) < 4):
    rclpy.spin_once(n, timeout_sec=0.1)
p = pose()
if p is None or len(S) < 4:
    print('준비 실패:', sorted(S.keys()))
    raise SystemExit(1)
tw = time.time()
while time.time() - tw < 15:
    try:
        buf.lookup_transform('base_link', S['pc'].header.frame_id, rclpy.time.Time())
        buf.lookup_transform('base_link', S['sc'].header.frame_id, rclpy.time.Time())
        break
    except Exception:
        rclpy.spin_once(n, timeout_sec=0.1)

print('로버 map (%.3f, %.3f) hd=%.2f deg' % (p[0], p[1], math.degrees(p[2])))
print('차체 0.50x0.33  패딩 %.2f → 유효 %.2fx%.2f  내접반경 %.3f  외접반경 %.3f'
      % (PAD, 2*(HL+PAD), 2*(HW+PAD), HW+PAD, math.hypot(HL+PAD, HW+PAD)))

# ── 센서 점을 base_link 로 ──────────────────────────────────────────
R, T = tfm('base_link', S['sc'].header.frame_id)
sc = S['sc']
r = np.array(sc.ranges)
ang = sc.angle_min + np.arange(len(r)) * sc.angle_increment
ok = np.isfinite(r) & (r > sc.range_min) & (r < sc.range_max)
L = np.stack([r[ok]*np.cos(ang[ok]), r[ok]*np.sin(ang[ok]), np.zeros(ok.sum())], 1) @ R.T + T
lid = L[:, :2]

R, T = tfm('base_link', S['pc'].header.frame_id)
m = S['pc']
off = {f.name: f.offset for f in m.fields}
raw = np.frombuffer(m.data, dtype=np.uint8).reshape(-1, m.point_step)
xyz = np.stack([raw[:, off[k]:off[k]+4].copy().view(np.float32).ravel() for k in ('x', 'y', 'z')], 1)
xyz = xyz[np.isfinite(xyz).all(1)]
P = xyz @ R.T + T
dep_obs = P[(P[:, 2] > 0.06) & (P[:, 2] < 0.40)][:, :2]          # 장애물 높이 깊이점
dep_all = P

print('센서 점: 라이다 %d, 깊이(장애물높이) %d' % (len(lid), len(dep_obs)))
print()

# ── A) 물리 통로 ───────────────────────────────────────────────────
print('########## A. 물리 통로 (센서 원시 점, 코스트맵 무관) ##########')
sel = P[(P[:, 2] > 0.05) & (P[:, 2] < 0.30) & (P[:, 0] > 0.2) & (P[:, 0] < 1.5) & (np.abs(P[:, 1]) < 0.6)]
box = None
if len(sel):
    o = sel[np.argsort(sel[:, 1])]
    cl, cur = [], [o[0]]
    for q in o[1:]:
        if q[1] - cur[-1][1] > 0.08:
            if len(cur) >= 25: cl.append(np.array(cur))
            cur = [q]
        else:
            cur.append(q)
    if len(cur) >= 25: cl.append(np.array(cur))
    low = sorted([(abs(float(np.median(c[:, 1]))), c) for c in cl if float(np.median(c[:, 2])) < 0.20], key=lambda t: t[0])
    if low:
        c = low[0][1]
        box = (float(np.percentile(c[:, 0], 5)), float(np.median(c[:, 1])), len(c))
if box:
    bx, by, bn = box
    print('상자: 전면 x=%.3f  중심 y=%+.3f  (%d점)  → x 구간 [%.2f, %.2f], y 구간 [%+.2f, %+.2f]'
          % (bx, by, bn, bx, bx+BOX_D, by-BOX_W/2, by+BOX_W/2))
    # 상자 x 구간(앞뒤 10cm 여유)에서 모든 장애물 점의 y
    x0, x1 = bx - 0.10, bx + BOX_D + 0.10
    ys = np.concatenate([lid[(lid[:, 0] > x0) & (lid[:, 0] < x1)][:, 1],
                         dep_obs[(dep_obs[:, 0] > x0) & (dep_obs[:, 0] < x1)][:, 1]])
    ys = np.sort(ys[np.abs(ys) < 1.5])
    print('  이 x 구간의 장애물 점 %d개 (라이다+깊이). y 정렬 후 10cm 넘는 빈 틈:' % len(ys))
    gaps = []
    for i in range(1, len(ys)):
        if ys[i] - ys[i-1] > 0.10:
            gaps.append((ys[i-1], ys[i]))
    if len(ys):
        gaps.insert(0, (-1.5, ys[0])); gaps.append((ys[-1], 1.5))
    print('   %-22s %-8s %-10s %-10s %s' % ('틈 [y_lo, y_hi]', '폭', '차체0.33', '패딩0.43', '허용 자세각(패딩)'))
    for a, b in gaps:
        w = b - a
        if w < 0.25 or abs(a) > 1.3 or abs(b) > 1.3: continue
        # 2(0.30 sinθ + 0.215 cosθ) <= w 를 만족하는 최대 θ
        th = 0.0
        for d in range(0, 91):
            t = math.radians(d)
            if 2*((HL+PAD)*math.sin(t) + (HW+PAD)*math.cos(t)) <= w: th = d
            else: break
        th_raw = 0.0
        for d in range(0, 91):
            t = math.radians(d)
            if 2*(HL*math.sin(t) + HW*math.cos(t)) <= w: th_raw = d
            else: break
        print('   [%+.2f, %+.2f]         %.2f m   %-10s %-10s %2d deg (패딩無 %2d deg)'
              % (a, b, w, '통과' if w >= 0.33 else '불가', '통과' if w >= 0.43 else '불가', th, th_raw))
else:
    print('상자 클러스터 못 찾음')
print()

# ── B) 코스트맵 감사 ─────────────────────────────────────────────
print('########## B. 코스트맵 LETHAL(100) 셀 vs 센서 점 ##########')
co, si = math.cos(p[2]), math.sin(p[2])
allpts = np.concatenate([lid, dep_obs]) if len(dep_obs) else lid
for key, name in (('lc', '로컬'), ('gc', '전역')):
    g = S[key]
    res = g.info.resolution
    ox, oy = g.info.origin.position.x, g.info.origin.position.y
    W, H = g.info.width, g.info.height
    data = np.array(g.data, dtype=np.int16).reshape(H, W)
    jj, ii = np.where(data >= LETHAL_PUB)
    mx = ox + (ii + 0.5) * res; my = oy + (jj + 0.5) * res
    # map → base_link
    dx, dy = mx - p[0], my - p[1]
    bx_ = dx*co + dy*si; by_ = -dx*si + dy*co
    near = (bx_ > -0.5) & (bx_ < 1.3) & (np.abs(by_) < 0.9)
    bx_, by_ = bx_[near], by_[near]
    if len(bx_) == 0:
        print('  %s: 범위 안 LETHAL 셀 없음' % name); continue
    cells = np.stack([bx_, by_], 1)
    d = np.sqrt(((cells[:, None, :] - allpts[None, :, :])**2).sum(2)).min(1)
    matched = (d < 0.08).sum()
    print('  %s: 전방 -0.5~1.3m x 좌우 0.9m 안 LETHAL 셀 %d개 중 센서 점 8cm 안에 있는 것 %d (%.0f%%), 없는 것 %d'
          % (name, len(cells), matched, 100.0*matched/len(cells), len(cells)-matched))
    orphan = cells[d >= 0.08]
    if len(orphan):
        # 고아 셀의 분포
        print('     근거 없는 셀 위치(차체좌표) 예: ' + ', '.join('(%+.2f,%+.2f)' % (a, b) for a, b in orphan[:8]))
        print('     근거 없는 셀 x 범위 %.2f~%.2f, y 범위 %+.2f~%+.2f' % (orphan[:, 0].min(), orphan[:, 0].max(), orphan[:, 1].min(), orphan[:, 1].max()))
print()

# ── C) 컨트롤러 기준으로 다시 본 통과 폭 ───────────────────────
print('########## C. 통과 폭 — 판정 기준 두 가지 비교 (전역 코스트맵) ##########')
g = S['gc']; res = g.info.resolution; ox, oy = g.info.origin.position.x, g.info.origin.position.y


def cost(mx, my):
    i = int((mx - ox) / res); j = int((my - oy) / res)
    if 0 <= i < g.info.width and 0 <= j < g.info.height:
        return g.data[j*g.info.width + i]
    return -1


def fp_max(lx, ly, th_extra=0.0):
    """footprint(+pad) 둘레 최대비용 — RPP 의 footprintCostAtPose 와 같은 방식(둘레)."""
    best = -1
    Lp, Wp = HL+PAD, HW+PAD
    c2, s2 = math.cos(p[2]+th_extra), math.sin(p[2]+th_extra)
    pts = []
    for k in range(13):
        t = k/12.0
        pts += [(-Lp + 2*Lp*t, -Wp), (-Lp + 2*Lp*t, Wp), (-Lp, -Wp + 2*Wp*t), (Lp, -Wp + 2*Wp*t)]
    cx = p[0] + lx*co - ly*si; cy = p[1] + lx*si + ly*co
    for fx, fy in pts:
        v = cost(cx + fx*c2 - fy*s2, cy + fx*s2 + fy*c2)
        if v > best: best = v
    return best


print('   전방x   기준1: 중심셀<99 (NavFn식)      기준2: footprint둘레<100 (RPP 실제)   기준3(오늘 오류): footprint<99')
w1min = w2min = w3min = (9.9, None)
for k in range(4, 33, 2):
    lx = 0.05*k
    runs = {1: [], 2: [], 3: []}
    cur = {1: None, 2: None, 3: None}
    for mm in range(-20, 21):
        ly = 0.05*mm
        mx = p[0] + lx*co - ly*si; my = p[1] + lx*si + ly*co
        v1 = cost(mx, my); v2 = fp_max(lx, ly)
        ok = {1: 0 <= v1 < INSCRIBED_PUB, 2: 0 <= v2 < LETHAL_PUB, 3: 0 <= v2 < INSCRIBED_PUB}
        for q in (1, 2, 3):
            if ok[q] and cur[q] is None: cur[q] = ly
            elif not ok[q] and cur[q] is not None: runs[q].append((cur[q], ly-0.05)); cur[q] = None
    for q in (1, 2, 3):
        if cur[q] is not None: runs[q].append((cur[q], 1.0))
    w = {q: max([b-a+0.05 for a, b in runs[q]], default=0.0) for q in (1, 2, 3)}
    if lx <= 1.6:
        if w[1] < w1min[0]: w1min = (w[1], lx)
        if w[2] < w2min[0]: w2min = (w[2], lx)
        if w[3] < w3min[0]: w3min = (w[3], lx)
    f = lambda q: (('[%+.2f~%+.2f]' % max(runs[q], key=lambda t: t[1]-t[0])) if runs[q] else '(없음)')
    print('   %.2f   %-22s %.2f    %-22s %.2f    %-22s %.2f' % (lx, f(1), w[1], f(2), w[2], f(3), w[3]))
print('   → 전방 1.6m 최소폭:  기준1 %.2f m (@%.2f)   기준2(RPP) %.2f m (@%.2f)   기준3(오류) %.2f m (@%.2f)'
      % (w1min[0], w1min[1], w2min[0], w2min[1], w3min[0], w3min[1]))
print()
print('   기준2 가 RPP 가 실제로 쓰는 것이다. 기준3 은 내접 반경을 두 번 세는 오류로,')
print('   오늘 "0.7~0.9 m 필요, 통과 불가" 라는 과장된 결론의 원인이다.')
