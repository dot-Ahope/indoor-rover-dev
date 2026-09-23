#!/usr/bin/env python3
"""F0-a 복귀 중단 분석 (09-23): 지정 시각들에서 로컬 코스트맵(odom) 치명 셀(OccupancyGrid 100 = LETHAL, 99 = 내접)과 차체 풋프린트(0.5×0.33) 최소 거리·위치,
   그리고 그 시각의 전역 경로(/plan, /plan_smoothed)가 x=1.0~1.4 구간에서 지나는 y(map). 인자: BAG T[,T...]"""
import sys, math, bisect
import numpy as np
import rosbag2_py
from rclpy.serialization import deserialize_message
from rosidl_runtime_py.utilities import get_message
def yaw(q): return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
BAG = sys.argv[1]; TS = [float(x) for x in sys.argv[2].split(',')]
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
def cells(g, thr):
    d = np.asarray(g.data, dtype=np.int16).reshape(g.info.height, g.info.width); iy, ix = np.nonzero(d >= thr)
    res = g.info.resolution; return g.info.origin.position.x + (ix + 0.5) * res, g.info.origin.position.y + (iy + 0.5) * res
def fp_dist(px, py, rx, ry, rth):
    # 셀 → 차체 좌표, 직사각 [-0.25,0.25]×[-0.165,0.165] 까지 거리(안이면 음수 대신 0)
    c, s = math.cos(rth), math.sin(rth); dx, dy = px - rx, py - ry
    bx, by = c * dx + s * dy, -s * dx + c * dy
    ex, ey = np.maximum(np.abs(bx) - 0.25, 0), np.maximum(np.abs(by) - 0.165, 0)
    return np.hypot(ex, ey), bx, by
for T in TS:
    _, ox, oy, oth = last(ob, T); _, mx, my, mth = last(mo, T)
    tl, g = last(lc, T)
    print('== t=%.2f  odom (%.3f, %.3f, %.1f°)  로컬맵 나이 %.2f s' % (T, ox, oy, math.degrees(oth), T - tl))
    for thr, name in ((100, 'LETHAL'), (99, 'INSCRIBED+'), (60, 'cost>=60')):
        px, py = cells(g, thr); d, bx, by = fp_dist(px, py, ox, oy, oth)
        k = np.argsort(d)[:6]
        if thr == 100:
            for side, msk in (('왼쪽(by>0)', by > 0.165), ('오른쪽(by<0)', by < -0.165)):
                if msk.any(): j = np.argmin(np.where(msk, d, 9)); print('  LETHAL %s 최소 %.3f m @차체(%+.2f,%+.2f) map≈(%.2f,%.2f)' % (side, d[j], bx[j], by[j], px[j] + mx, py[j] + my))
        print('  %-10s 셀 %d | 차체까지 최소 %.3f m | 가까운 셀(차체좌표 앞+/왼+): %s' % (name, len(d), d.min() if len(d) else float('nan'), ' '.join('(%+.2f,%+.2f %.3f)' % (bx[i], by[i], d[i]) for i in k)))
    for nm, arr in (('plan', pl), ('smoothed', ps)):
        if not arr: continue
        tp_, pts = last(arr, T); sel = [p for p in pts if 0.9 <= p[0] <= 1.5]
        if sel: print('  %s(%.1f s 전) x0.9~1.5 구간 y: %.3f~%.3f' % (nm, T - tp_, min(p[1] for p in sel), max(p[1] for p in sel)))
    tg, gg = last(gc, T); px, py = cells(gg, 100)
    sel = (px > 1.0) & (px < 1.5) & (py > -0.4) & (py < 0.4)
    if sel.any(): print('  전역 LETHAL 상자 부근(map): x %.3f~%.3f y %.3f~%.3f (%d 셀)' % (px[sel].min(), px[sel].max(), py[sel].min(), py[sel].max(), sel.sum()))
