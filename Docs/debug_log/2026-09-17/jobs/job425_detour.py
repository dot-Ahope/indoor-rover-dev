#!/usr/bin/env python3
"""'상자를 크게 돌아간다' 분석 (2026-09-17 §15, 사용자 질문). 로버는 움직이지 않는다. 인자: BAG GOAL_EPOCH [variants=1]
  A. 전역 경로(/plan, NavFn 원출력) vs 실제 궤적(map) 의 횡 위치 — 경로가 넓게 도는가, 컨트롤러가 더 도는가
  B. 전역 코스트맵 단면(x 0.6/0.9/1.2/1.5, y −0.5~+0.9) — 비용 골짜기 위치, 좌우 LETHAL 경계
  C. NavFn 근사 재현(8-이웃 Dijkstra, 비용 = 50 + 0.8·c, 253↑ 통과불가, 미지 253) → 실제 /plan 과 비교해 근사 검증
  D. 같은 LETHAL 셀로 inflation 반경·감쇠를 바꿔 다시 팽창·계획 → 차선변경 시작 x, 상자 옆 횡 위치, 최대 진행각, 상자 옆 여유
"""
import sys, math, heapq
import numpy as np
import rosbag2_py
from rclpy.serialization import deserialize_message
from tf2_msgs.msg import TFMessage
from nav_msgs.msg import OccupancyGrid, Path

BAG, G = sys.argv[1], float(sys.argv[2]); VARIANTS = len(sys.argv) > 3 and sys.argv[3] == '1'
INSCR = 0.165 + 0.01          # 전역: 반폭 + footprint_padding


def yaw_of(q):
    return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))


r = rosbag2_py.SequentialReader(); r.open(rosbag2_py.StorageOptions(uri=BAG, storage_id='sqlite3'), rosbag2_py.ConverterOptions('', ''))
plans, gcs, mo, ob = [], [], [], []
while r.has_next():
    topic, data, ts = r.read_next(); t = ts * 1e-9 - G
    if topic == '/plan':
        m = deserialize_message(data, Path); plans.append((t, np.array([[p.pose.position.x, p.pose.position.y] for p in m.poses])))
    elif topic == '/global_costmap/costmap':
        gcs.append((t, deserialize_message(data, OccupancyGrid)))
    elif topic == '/tf':
        for tr in deserialize_message(data, TFMessage).transforms:
            st = tr.header.stamp.sec + tr.header.stamp.nanosec * 1e-9 - G
            if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom':
                mo.append((st, tr.transform.translation.x, tr.transform.translation.y, yaw_of(tr.transform.rotation)))
            elif tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link':
                ob.append((st, tr.transform.translation.x, tr.transform.translation.y, yaw_of(tr.transform.rotation)))
mo.sort(); ob.sort()
mot = np.array([m[0] for m in mo])
traj = []
for (t, x, y, th) in ob:
    if t < -1:
        continue
    k = min(max(np.searchsorted(mot, t) - 1, 0), len(mo) - 1); _, ax, ay, ath = mo[k]
    traj.append((t, ax + x * math.cos(ath) - y * math.sin(ath), ay + x * math.sin(ath) + y * math.cos(ath)))
traj = np.array(traj)
name = BAG.split('_')[-1]
XG = np.round(np.arange(0.0, 2.01, 0.1), 2)


def y_at(P, xs):
    out = []
    for x in xs:
        d = np.abs(P[:, 0] - x); i = int(np.argmin(d))
        out.append(P[i, 1] if d[i] < 0.06 else float('nan'))
    return np.array(out)


def heading_max(P):
    d = np.diff(P, axis=0); s = np.hypot(d[:, 0], d[:, 1]) > 1e-6
    if s.sum() < 5:
        return float('nan')
    ang = np.degrees(np.arctan2(d[s, 1], d[s, 0]))
    k = 4
    sm = np.convolve(ang, np.ones(k) / k, mode='valid')
    return float(np.max(np.abs(sm)))


print('==== %s ====' % name)
p0 = [p for p in plans if p[0] >= 0][0]; pm = min(plans, key=lambda p: abs(p[0] - 10.0))
print('A. 횡 위치 y (map, x 0.0~2.0 m 0.1 간격)')
print('   x             ' + ' '.join('%5.1f' % x for x in XG))
print('   /plan t=%4.1f  ' % p0[0] + ' '.join('%+5.2f' % v for v in y_at(p0[1], XG)) + '  | 최대 진행각 %.0f°' % heading_max(p0[1]))
print('   /plan t=%4.1f  ' % pm[0] + ' '.join('%+5.2f' % v for v in y_at(pm[1], XG)) + '  | 최대 진행각 %.0f°' % heading_max(pm[1]))
print('   궤적(실제)     ' + ' '.join('%+5.2f' % v for v in y_at(traj[:, 1:3], XG)) + '  | 최대 진행각 %.0f°' % heading_max(traj[::5, 1:3]))

gc = min(gcs, key=lambda g: abs(g[0] - 10.0)); M = gc[1]
res = M.info.resolution; ox, oy = M.info.origin.position.x, M.info.origin.position.y; W, H = M.info.width, M.info.height
occ = np.array(M.data, dtype=np.int16).reshape(H, W)
c2 = np.zeros((H, W), dtype=np.float64)
c2[occ == 100] = 254; c2[occ == 99] = 253; c2[occ < 0] = 255
mid = (occ >= 1) & (occ <= 98); c2[mid] = np.round(1 + (occ[mid] - 1) * 251.0 / 97.0)


def ci(x):
    return int(math.floor((x - ox) / res))


def cj(y):
    return int(math.floor((y - oy) / res))


print('B. 전역 코스트맵 단면 (t=%.1f, 비용 0~252, # LETHAL, o 내접 253, ? 미지; y −0.50 → +0.90, 0.05 간격)' % gc[0])
YS = np.round(np.arange(-0.50, 0.901, 0.05), 2)
print('   y    ' + ''.join('%4.0f' % (100 * y) for y in YS) + '  (cm)')
for xq in (0.3, 0.6, 0.9, 1.2, 1.5, 1.8):
    row = []
    for yq in YS:
        v = c2[cj(yq), ci(xq)]
        row.append('   #' if v == 254 else '   o' if v == 253 else '   ?' if v == 255 else '%4d' % v)
    free = [(yq, c2[cj(yq), ci(xq)]) for yq in YS if c2[cj(yq), ci(xq)] < 253]
    low = min(free, key=lambda z: z[1]) if free else (float('nan'), 0)
    print('   x=%.1f%s | 최저 %d @ y %+.2f' % (xq, ''.join(row), low[1], low[0]))

leth = np.argwhere(occ == 100)


def inflate(R, k):
    n = int(math.ceil(R / res))
    dist = np.full((H, W), np.inf)
    for (j, i) in leth:
        j0, j1, i0, i1 = max(j - n, 0), min(j + n + 1, H), max(i - n, 0), min(i + n + 1, W)
        jj, ii = np.mgrid[j0:j1, i0:i1]
        d = np.hypot(jj - j, ii - i) * res
        dist[j0:j1, i0:i1] = np.minimum(dist[j0:j1, i0:i1], d)
    cost = np.where(dist <= INSCR, 253.0, np.where(dist <= R, np.floor(252.0 * np.exp(-k * (dist - INSCR))), 0.0))
    cost[dist == 0] = 254.0
    cost[(occ < 0) & (cost == 0)] = 255.0
    return cost, dist


def navfn_like(cost):
    nav = np.where(cost < 253, 50.0 + 0.8 * cost, np.where(cost == 255, 253.0, np.inf))
    sj, si = cj(0.0), ci(0.0); gj, gi = cj(0.0), ci(2.0)
    D = np.full((H, W), np.inf); D[sj, si] = 0; prev = {}
    hq = [(0.0, sj, si)]
    nb = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    while hq:
        d, j, i = heapq.heappop(hq)
        if d > D[j, i]:
            continue
        if (j, i) == (gj, gi):
            break
        for dj, di in nb:
            a, b = j + dj, i + di
            if 0 <= a < H and 0 <= b < W and np.isfinite(nav[a, b]):
                nd = d + 0.5 * (nav[j, i] + nav[a, b]) * math.hypot(dj, di)
                if nd < D[a, b]:
                    D[a, b] = nd; prev[(a, b)] = (j, i); heapq.heappush(hq, (nd, a, b))
    if (gj, gi) not in prev:
        return None
    pts = [(gj, gi)]
    while pts[-1] != (sj, si):
        pts.append(prev[pts[-1]])
    return np.array([[ox + (i + 0.5) * res, oy + (j + 0.5) * res] for j, i in pts[::-1]])


def summarize(label, P, dist):
    ys = y_at(P, XG)
    onset = next((x for x, v in zip(XG, ys) if not math.isnan(v) and abs(v) > 0.05), float('nan'))
    box = (P[:, 0] > 1.1) & (P[:, 0] < 1.35)
    lat_box = float(np.median(P[box, 1])) if box.any() else float('nan')
    clr = min(dist[cj(y), ci(x)] for x, y in P[box]) - 0.165 if box.any() else float('nan')
    print('   %-24s 차선변경 시작 x %.1f | 상자옆 횡 %+.3f · LETHAL셀−반폭 %.3f m | 최대 진행각 %2.0f° | y(x .2~1.8): %s' % (
        label, onset, lat_box, clr, heading_max(P), ' '.join('%+5.2f' % v for v in ys[2:19:2])))


print('C/D. NavFn 근사(8-이웃 Dijkstra, 격자 계단 있음) vs 실제')
_, dist0 = inflate(0.70, 2.0)
summarize('실제 /plan t=%.1f' % p0[0], p0[1], dist0)
P_real = navfn_like(c2)
if P_real is not None:
    summarize('근사: bag 코스트맵 그대로', P_real, dist0)
if VARIANTS:
    for R, k in ((0.70, 2.0), (0.55, 2.0), (0.40, 2.0), (0.30, 2.0), (0.70, 4.0), (0.55, 4.0), (0.40, 4.0), (0.70, 8.0)):
        cost, dist = inflate(R, k)
        P = navfn_like(cost)
        if P is None:
            print('   근사: 재팽창 R %.2f k %.1f 경로 없음' % (R, k))
        else:
            summarize('근사: 재팽창 R%.2f k%.1f' % (R, k), P, dist)
    print('   참고 inflation 비용 c(d)=252·exp(−k(d−0.175)), d≤R:')
    for R, k in ((0.70, 2.0), (0.40, 2.0), (0.70, 4.0)):
        print('     R%.2f k%.1f: ' % (R, k) + '  '.join('d%.2f→%3d' % (d, int(252 * math.exp(-k * (d - INSCR))) if d <= R else 0) for d in (0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.71)))
