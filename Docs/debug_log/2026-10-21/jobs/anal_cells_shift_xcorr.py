#!/usr/bin/env python3
"""anal_cells_shift_xcorr — 두 시각의 전역 LETHAL 칸(저장 지도 칸 제외) 집합을 겹쳐, 가장 잘 겹치는 이동량을 찾는다. (2026-10-21 §13, PC)
  가설: map→odom 이 바뀌면 nvblox 기억(odom 좌표)이 map 좌표에서 통째로 옮겨 찍힌다 → 최적 이동 ≈ 그 사이 map→odom 변화.
  인자: bag t1 t2 [창 x0,x1,y0,y1]"""
import sys, math, bisect
from pathlib import Path
import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
bag, t1, t2 = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
W = [float(v) for v in sys.argv[4].split(',')] if len(sys.argv) > 4 else [-1.5, 3.5, -2.5, 1.5]
yaw = lambda q: math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
GC, MP, MO = [], None, []
with AnyReader([Path(bag)], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
    t0 = rd.start_time * 1e-9
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/global_costmap/costmap', '/map', '/tf')]):
        m = rd.deserialize(raw, c.msgtype); tt = t * 1e-9 - t0
        if c.topic == '/tf':
            for tr in m.transforms:
                if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom': MO.append((tt, (tr.transform.translation.x, tr.transform.translation.y, yaw(tr.transform.rotation))))
        else:
            g = m.info; A = np.array(m.data, dtype=np.int16).reshape(g.height, g.width)
            if c.topic == '/map': MP = (g.origin.position.x, g.origin.position.y, g.resolution, A)
            else: GC.append((tt, g.origin.position.x, g.origin.position.y, g.resolution, A))
MO.sort(key=lambda q: q[0]); MOt = [q[0] for q in MO]; at = lambda t: MO[max(bisect.bisect_right(MOt, t) - 1, 0)][1]
mx, my, mr, MA = MP; mys, mxs = np.nonzero(MA >= 65); MPt = np.c_[mx + (mxs + 0.5) * mr, my + (mys + 0.5) * mr]
def cells(tq):
    k = max(bisect.bisect_right([g[0] for g in GC], tq) - 1, 0); tg, ox, oy, r, A = GC[k]
    ys, xs = np.nonzero(A >= 100); P = np.c_[ox + (xs + 0.5) * r, oy + (ys + 0.5) * r]
    P = P[(P[:, 0] >= W[0]) & (P[:, 0] <= W[1]) & (P[:, 1] >= W[2]) & (P[:, 1] <= W[3])]
    keep = np.array([np.hypot(MPt[:, 0] - p[0], MPt[:, 1] - p[1]).min() > 0.10 for p in P]); return tg, P[keep], r
ta, A, r = cells(t1); tb, B, _ = cells(t2)
SA = {(round(p[0] / r), round(p[1] / r)) for p in A}; SB = {(round(p[0] / r), round(p[1] / r)) for p in B}
best = []
for dx in range(-12, 13):
    for dy in range(-12, 13):
        best.append((len({(x + dx, y + dy) for x, y in SA} & SB), dx * r, dy * r))
best.sort(reverse=True)
a1, a2 = at(ta), at(tb)
print('bag %s · t1=%.1f s 지도 밖 LETHAL %d 칸 · t2=%.1f s %d 칸 · 그대로 겹침 %d' % (Path(bag).name, ta, len(SA), tb, len(SB), len(SA & SB)))
print('map→odom t1 (%.3f, %.3f, %+.2f°) → t2 (%.3f, %.3f, %+.2f°) · 변화 (%+.3f, %+.3f, %+.2f°)' % (a1[0], a1[1], math.degrees(a1[2]), a2[0], a2[1], math.degrees(a2[2]), a2[0] - a1[0], a2[1] - a1[1], math.degrees(a2[2] - a1[2])))
print('가장 잘 겹치는 이동 상위 5:', ' · '.join('(%+.2f, %+.2f) %d 칸' % (dx, dy, n) for n, dx, dy in best[:5]))
