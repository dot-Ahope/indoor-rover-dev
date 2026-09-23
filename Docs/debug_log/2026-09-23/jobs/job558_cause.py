#!/usr/bin/env python3
"""F0-a 중단 원인 분석 (09-23) — bag_f0a1 만으로.
 원인1(복귀 경로가 상자에 붙은 이유): 전역 코스트맵 단면(x=1.15/1.20/1.25, y −0.30~0.80) 출발·복귀 시각 비교 + 출발·복귀 첫 경로의 상자 옆 y·경로 비용.
 원인2(여유 5 cm 에서 MPPI 전 궤적 충돌): 중단 순간 로컬 코스트맵에서 Nav2 FootprintCollisionChecker 와 같은 방식
   (패딩 0.01 풋프린트 꼭짓점 → 셀, 변마다 Bresenham, 최대 비용)으로 현 자세·전진·회전 조합의 충돌 여부.
 그림용 JSON(/tmp/f0a1_vis.json)도 쓴다. 인자: BAG"""
import sys, math, bisect, json
import numpy as np
import rosbag2_py
from rclpy.serialization import deserialize_message
from rosidl_runtime_py.utilities import get_message


def yaw(q): return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))


BAG = sys.argv[1]
T0, T2, TA = 1790141867.39, 1790141904.24, 1790141915.70   # 목표1 시작, 목표2 시작, 첫 중단 (nav2.log)
r = rosbag2_py.SequentialReader(); r.open(rosbag2_py.StorageOptions(uri=BAG, storage_id='sqlite3'), rosbag2_py.ConverterOptions('cdr', 'cdr'))
types = {t.name: t.type for t in r.get_all_topics_and_types()}
ob, mo, lc, gc, pl, ps = [], [], [], [], [], []
while r.has_next():
    tp, data, ts = r.read_next(); t = ts * 1e-9
    if tp not in ('/tf', '/local_costmap/costmap', '/global_costmap/costmap', '/plan', '/plan_smoothed'): continue
    m = deserialize_message(data, get_message(types[tp]))
    if tp == '/tf':
        for tr in m.transforms:
            p = (t, tr.transform.translation.x, tr.transform.translation.y, yaw(tr.transform.rotation))
            if tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link': ob.append(p)
            elif tr.header.frame_id == 'map' and tr.child_frame_id == 'odom': mo.append(p)
    elif tp.startswith('/local'): lc.append((t, m))
    elif tp.startswith('/global'): gc.append((t, m))
    elif tp == '/plan': pl.append((t, [(q.pose.position.x, q.pose.position.y) for q in m.poses]))
    else: ps.append((t, [(q.pose.position.x, q.pose.position.y) for q in m.poses]))


def last(arr, t):
    k = bisect.bisect_right([a[0] for a in arr], t) - 1; return arr[max(k, 0)]


def first_after(arr, t):
    k = bisect.bisect_left([a[0] for a in arr], t); return arr[min(k, len(arr) - 1)]


def grid(g): return np.asarray(g.data, dtype=np.int16).reshape(g.info.height, g.info.width)


def cost_at(g, d, x, y):
    i = int((x - g.info.origin.position.x) / g.info.resolution); j = int((y - g.info.origin.position.y) / g.info.resolution)
    return int(d[j, i]) if 0 <= i < g.info.width and 0 <= j < g.info.height else -2


def od2mp(tf, x, y):
    _, tx, ty, th = tf; c, s = math.cos(th), math.sin(th); return tx + c * x - s * y, ty + s * x + c * y


print('== 원인 1: 전역 코스트맵 단면 (OccupancyGrid 0~100; 100 = LETHAL, 99 = 내접) ==')
YS = [round(-0.30 + 0.05 * k, 2) for k in range(23)]
print('  y(map)             ' + ' '.join('%4.2f' % y if y >= 0 else '%4.1f' % y for y in YS))
for lab, t in (('출발 t+12', T0 + 12), ('복귀 시작', T2 + 0.5), ('복귀 t+8', T2 + 8)):
    tg, g = last(gc, t); d = grid(g)
    for x in (1.15, 1.20, 1.25):
        print('  %-9s x%.2f  ' % (lab, x) + ' '.join('%4d' % cost_at(g, d, x, y) for y in YS))


def plan_stats(arr, t, g):
    tp_, pts = first_after(arr, t); d = grid(g)
    near = [p for p in pts if 1.05 <= p[0] <= 1.35]
    c = [cost_at(g, d, x, y) for x, y in pts]
    return tp_, pts, (min(p[1] for p in near), max(p[1] for p in near)) if near else None, sum(max(v, 0) for v in c) / max(len(c), 1)


for lab, t in (('출발 첫 경로', T0), ('복귀 첫 경로', T2), ('복귀 t+8 경로', T2 + 8)):
    g = last(gc, t + 0.3)[1]
    for nm, arr in (('plan', pl), ('smoothed', ps)):
        tp_, pts, yr, mc = plan_stats(arr, t, g)
        print('  %-12s %-8s  상자 옆(x1.05~1.35) y %s | 경로 평균 비용 %.1f | 점 %d' % (lab, nm, '%.3f~%.3f' % yr if yr else '-', mc, len(pts)))

print('\n== 원인 2: 중단 순간 풋프린트 충돌 판정 (로컬 코스트맵, 패딩 0.01) ==')
tl, g = last(lc, TA); d = grid(g); res = g.info.resolution; ox_, oy_ = g.info.origin.position.x, g.info.origin.position.y
_, rx, ry, rth = last(ob, TA)
FP = [(0.26, 0.175), (0.26, -0.175), (-0.26, -0.175), (-0.26, 0.175)]


def fp_cost(x, y, th):
    c, s = math.cos(th), math.sin(th); cells = []
    for (a, b) in FP:
        wx, wy = x + c * a - s * b, y + s * a + c * b; cells.append((int((wx - ox_) / res), int((wy - oy_) / res)))
    mx = 0; hit = []
    for k in range(4):
        (x0, y0), (x1, y1) = cells[k], cells[(k + 1) % 4]
        dx, dy = abs(x1 - x0), -abs(y1 - y0); sx = 1 if x0 < x1 else -1; sy = 1 if y0 < y1 else -1; err = dx + dy; cx, cy = x0, y0
        while True:
            v = int(d[cy, cx]) if 0 <= cx < g.info.width and 0 <= cy < g.info.height else 100
            if v > mx: mx = v
            if v >= 100: hit.append((cx, cy))
            if cx == x1 and cy == y1: break
            e2 = 2 * err
            if e2 >= dy: err += dy; cx += sx
            if e2 <= dx: err += dx; cy += sy
    return mx, hit


m0, h0 = fp_cost(rx, ry, rth)
print('  로컬맵 나이 %.2f s | 현 자세 odom (%.3f, %.3f, %.1f°) 풋프린트 최대 비용 %d %s' % (TA - tl, rx, ry, math.degrees(rth), m0, '(LETHAL 셀 %d)' % len(h0) if h0 else ''))
ANG = (-10, -7.5, -5, -2.5, 0, 2.5, 5, 7.5, 10)
print('  전진 dx(m) / 회전 dθ(°, +왼쪽) → ' + ' '.join('%5.1f' % a for a in ANG))
tab = []
for dxm in (-0.05, 0.0, 0.05, 0.10, 0.15, 0.20, 0.25):
    row = []
    for da in ANG:
        th = rth + math.radians(da); v, _ = fp_cost(rx + dxm * math.cos(rth), ry + dxm * math.sin(rth), th); row.append(v)
    tab.append((dxm, row)); print('    %+.2f                          ' % dxm + ' '.join('%5s' % ('X' if v >= 100 else v) for v in row))

tfA = last(mo, TA)


def cells_map(g, d, tf=None, box=(0.3, 2.3, -0.6, 1.0), thr=1):
    iy, ix = np.nonzero(d >= thr); x = g.info.origin.position.x + (ix + 0.5) * g.info.resolution; y = g.info.origin.position.y + (iy + 0.5) * g.info.resolution
    out = []
    for a, b, v in zip(x, y, d[iy, ix]):
        if tf is not None: a, b = od2mp(tf, a, b)
        if box[0] <= a <= box[1] and box[2] <= b <= box[3]: out.append((round(float(a), 3), round(float(b), 3), int(v)))
    return out


gA = last(gc, T2 + 0.5)[1]; gO = last(gc, T0 + 12)[1]
traj = []
for (t, x, y, th) in ob:
    if T0 <= t <= TA + 1 and (not traj or t - traj[-1][0] > 0.2):
        tf = last(mo, t); mx_, my_ = od2mp(tf, x, y); traj.append((t, round(mx_, 3), round(my_, 3), round(th + tf[3], 3)))
ax, ay = od2mp(tfA, rx, ry)
vis = {'global_out': cells_map(gO, grid(gO)), 'global_ret': cells_map(gA, grid(gA)), 'local_abort': cells_map(g, d, tfA, thr=99),
       'plan_out': first_after(ps, T0)[1], 'plan_ret': first_after(ps, T2)[1], 'plan_ret_raw': first_after(pl, T2)[1],
       'traj': [(p[1], p[2], p[3], 1 if p[0] >= T2 else 0) for p in traj], 'abort': (round(ax, 3), round(ay, 3), round(rth + tfA[3], 4)),
       'fp_table': tab, 'fp_angles': ANG, 'fp_now': m0}
json.dump(vis, open('/tmp/f0a1_vis.json', 'w'))
print('  그림 데이터 /tmp/f0a1_vis.json (셀 전역 %d/%d, 로컬 %d)' % (len(vis['global_out']), len(vis['global_ret']), len(vis['local_abort'])))
