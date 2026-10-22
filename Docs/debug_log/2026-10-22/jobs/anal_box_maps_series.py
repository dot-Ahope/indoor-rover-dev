#!/usr/bin/env python3
"""anal_box_maps_series — 상자 영역(기록 상자 ±0.05 m) 칸 수를 세 지도에서 시간 묶음별로: nvblox 조각 · 로컬 코스트맵 LETHAL · 전역 코스트맵 LETHAL, 로버 위치 · 상자까지 거리 · 방위(2026-10-22 §13, PC).
  왜: f2lp1 접촉 순간 세 지도 모두 상자 칸 0 — 언제부터 상자를 잃었고, 복귀 중 다시 본 적이 있는지.
  인자: bag 시작s 끝s [묶음 s=5]"""
import sys, math, bisect
from pathlib import Path
import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore, get_types_from_msg
TS = get_typestore(Stores.ROS2_HUMBLE)
TS.register(get_types_from_msg('std_msgs/Header header\nfloat32 resolution\nuint32 width\nuint32 height\ngeometry_msgs/Point origin\nfloat32 unknown_value\nfloat32[] data\n', 'nvblox_msgs/msg/DistanceMapSlice'))
bag, TA, TB = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]); W = float(sys.argv[4]) if len(sys.argv) > 4 else 5
BOX = (1.151, 1.261, -0.20, -0.02); REG = (BOX[0] - 0.05, BOX[1] + 0.05, BOX[2] - 0.05, BOX[3] + 0.05); BC = (1.206, -0.11)
yq = lambda q: math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
def comp(a, b):
    c, s = math.cos(a[2]), math.sin(a[2]); return (a[0] + c * b[0] - s * b[1], a[1] + s * b[0] + c * b[1], a[2] + b[2])
MO, OB, EV = [], [], []
with AnyReader([Path(bag)], default_typestore=TS) as rd:
    T0 = rd.start_time * 1e-9
    want = ('/tf', '/local_costmap/costmap', '/global_costmap/costmap', '/nvblox_node/static_map_slice')
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in want]):
        tt = t * 1e-9 - T0
        if c.topic != '/tf' and not (TA <= tt <= TB): continue
        m = rd.deserialize(raw, c.msgtype)
        if c.topic == '/tf':
            for tr in m.transforms:
                v = (tr.transform.translation.x, tr.transform.translation.y, yq(tr.transform.rotation))
                if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom': MO.append((tt, v))
                elif tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link': OB.append((tt, v))
        elif c.topic.endswith('costmap'):
            g = m.info; A = np.array(m.data, np.int16).reshape(g.height, g.width); ys, xs = np.nonzero(A >= 100)
            EV.append((tt, 'L' if c.topic.startswith('/local') else 'G', m.header.frame_id, np.c_[g.origin.position.x + (xs + .5) * g.resolution, g.origin.position.y + (ys + .5) * g.resolution]))
        else:
            d = np.array(m.data, np.float32).reshape(m.height, m.width); iy, ix = np.nonzero((d <= 0) & (d != m.unknown_value)); r = m.resolution
            EV.append((tt, 'S', m.header.frame_id, np.c_[m.origin.x + (ix + .5) * r, m.origin.y + (iy + .5) * r]))
for L in (MO, OB): L.sort(key=lambda q: q[0])
MOt = [q[0] for q in MO]; OBt = [q[0] for q in OB]; at = lambda L, Lt, t: L[max(bisect.bisect_right(Lt, t) - 1, 0)][1]
B = {}
for tt, k, fr, P in EV:
    if fr == 'odom':
        mo = at(MO, MOt, tt); c, s = math.cos(mo[2]), math.sin(mo[2]); P = np.c_[mo[0] + c * P[:, 0] - s * P[:, 1], mo[1] + s * P[:, 0] + c * P[:, 1]]
    n = int(np.sum((P[:, 0] >= REG[0]) & (P[:, 0] <= REG[1]) & (P[:, 1] >= REG[2]) & (P[:, 1] <= REG[3])))
    B.setdefault(int((tt - TA) // W), {}).setdefault(k, []).append(n)
print('bag %s · t %.0f~%.0f s · 상자 영역 칸 수(묶음 안 최대) · 조각 S · 로컬 L · 전역 G' % (Path(bag).name, TA, TB))
for i in sorted(B):
    t = TA + i * W; p = comp(at(MO, MOt, t + W / 2), at(OB, OBt, t + W / 2)); d = math.hypot(BC[0] - p[0], BC[1] - p[1])
    b = math.degrees(math.atan2(math.sin(math.atan2(BC[1] - p[1], BC[0] - p[0]) - p[2]), math.cos(math.atan2(BC[1] - p[1], BC[0] - p[0]) - p[2])))
    g = lambda k: max(B[i].get(k, [-1]))
    print('  t %6.1f | S %3d · L %3d · G %3d | 로버 (%5.2f, %5.2f, %4.0f°) 상자 %.2f m 방위 %+4.0f°%s' % (t, g('S'), g('L'), g('G'), p[0], p[1], math.degrees(p[2]), d, b, '  ← 시야(±43°·1.4 m)' if d <= 1.4 and abs(b) <= 43 else ''))
