#!/usr/bin/env python3
"""anal_box_series — 출발점 낮은 상자 영역(1.15~1.35, -0.20~0.05) 로컬 LETHAL 칸 수와 로버-상자 거리를 10 s 묶음으로(주행 전체). (2026-10-22 §3, PC)
  인자: bag"""
import sys, math, bisect, numpy as np
from pathlib import Path
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
yaw = lambda q: math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
def comp(a, b):
    c, s = math.cos(a[2]), math.sin(a[2]); return (a[0] + c * b[0] - s * b[1], a[1] + s * b[0] + c * b[1], a[2] + b[2])
MO, OB, LC = [], [], []
with AnyReader([Path(sys.argv[1])], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
    t0 = rd.start_time * 1e-9
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/tf', '/local_costmap/costmap')]):
        tt = t * 1e-9 - t0; m = rd.deserialize(raw, c.msgtype)
        if c.topic == '/tf':
            for tr in m.transforms:
                a = (tr.transform.translation.x, tr.transform.translation.y, yaw(tr.transform.rotation))
                if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom': MO.append((tt, a))
                elif tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link': OB.append((tt, a))
        else:
            g = m.info; LC.append((tt, g.origin.position.x, g.origin.position.y, g.resolution, np.array(m.data, dtype=np.int16).reshape(g.height, g.width)))
MO.sort(key=lambda q: q[0]); OB.sort(key=lambda q: q[0]); MOt = [q[0] for q in MO]; OBt = [q[0] for q in OB]
at = lambda L, Lt, t: L[max(bisect.bisect_right(Lt, t) - 1, 0)][1]
print('%s | t(s) 묶음 | 상자 칸 최소~최대 | 로버-상자 거리 최소 m' % Path(sys.argv[1]).name)
for k in range(0, int(LC[-1][0]) + 1, 10):
    ns, ds = [], []
    for tt, ox, oy, r, A in LC:
        if not (k <= tt < k + 10): continue
        ys, xs = np.nonzero(A >= 100); a = at(MO, MOt, tt); c, s = math.cos(a[2]), math.sin(a[2])
        px, py = ox + (xs + .5) * r, oy + (ys + .5) * r; X, Y = a[0] + c * px - s * py, a[1] + s * px + c * py
        ns.append(int(np.sum((X >= 1.15) & (X <= 1.35) & (Y >= -0.20) & (Y <= 0.05))))
        p = comp(a, at(OB, OBt, tt)); ds.append(math.hypot(1.25 - p[0], -0.075 - p[1]))
    if ns: print('%3d~%3d | %2d~%2d | %.2f' % (k, k + 10, min(ns), max(ns), min(ds)))
