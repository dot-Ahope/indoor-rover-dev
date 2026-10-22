#!/usr/bin/env python3
"""anal_cell_timeline — 지정 칸들이 nvblox 조각에서 장애물이었던 시간 구간과, 그 구간에 상자가 카메라에 보였는지(2026-10-22 §11.2, PC).
  왜: 사용자 — "출발 시 기억하던 셀을 복귀 시 다시 찍은 것인가?" → 복귀 때 상자 밖 칸이 (가) 70~72 s 부터 이어진 기억인지 (나) 복귀 중 다시 보고 새로 찍은 것인지.
  '보임' = 상자 중심이 로버 진행 방향 ±43°(D455 깊이 수평 시야 절반) 안 · 1.4 m(통합 거리) 안. 구간은 0.5 s 넘게 끊기면 나눔.
  또 출발 기억(t 1.1 s, odom)이 map→odom 보정으로 옮겨 갔을 지도 위치도 시각별로 같이 냄.
  인자: 주행bag 칸들 'x,y;x,y'(칸 왼아래, 0.05 m)"""
import sys, math, bisect
from pathlib import Path
import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore, get_types_from_msg
TS = get_typestore(Stores.ROS2_HUMBLE)
TS.register(get_types_from_msg('std_msgs/Header header\nfloat32 resolution\nuint32 width\nuint32 height\ngeometry_msgs/Point origin\nfloat32 unknown_value\nfloat32[] data\n', 'nvblox_msgs/msg/DistanceMapSlice'))
BC = ((1.151 + 1.261) / 2, (-0.20 - 0.02) / 2); C = 0.05
bag = sys.argv[1]; Q = [tuple(int(round(float(v) / C)) for v in s.split(',')) for s in sys.argv[2].split(';')]
yq = lambda q: math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
def comp(a, b):
    c, s = math.cos(a[2]), math.sin(a[2]); return (a[0] + c * b[0] - s * b[1], a[1] + s * b[0] + c * b[1], a[2] + b[2])
MO, OB, SL = [], [], []
with AnyReader([Path(bag)], default_typestore=TS) as rd:
    T0 = rd.start_time * 1e-9
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/tf', '/nvblox_node/static_map_slice')]):
        m = rd.deserialize(raw, c.msgtype)
        if c.topic == '/tf':
            for tr in m.transforms:
                st = tr.header.stamp.sec + tr.header.stamp.nanosec * 1e-9; v = (tr.transform.translation.x, tr.transform.translation.y, yq(tr.transform.rotation))
                if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom': MO.append((st, v))
                elif tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link': OB.append((st, v))
        else:
            st = m.header.stamp.sec + m.header.stamp.nanosec * 1e-9
            d = np.array(m.data, np.float32).reshape(m.height, m.width); iy, ix = np.nonzero((d <= 0) & (d != m.unknown_value)); r = m.resolution
            SL.append((st, np.c_[m.origin.x + (ix + .5) * r, m.origin.y + (iy + .5) * r]))
MO.sort(); OB.sort(); MOt = [q[0] for q in MO]; OBt = [q[0] for q in OB]
at = lambda L, Lt, t: L[max(bisect.bisect_right(Lt, t) - 1, 0)][1]
a0 = at(MO, MOt, T0 + 1.1); dx, dy = BC[0] - a0[0], BC[1] - a0[1]; c0, s0 = math.cos(-a0[2]), math.sin(-a0[2]); bo = (c0 * dx - s0 * dy, s0 * dx + c0 * dy)
rows = {q: [] for q in Q}; vis = []
for st, P in SL:
    tt = st - T0; mo = at(MO, MOt, st); c, s = math.cos(mo[2]), math.sin(mo[2])
    cells = set(zip(np.floor((mo[0] + c * P[:, 0] - s * P[:, 1]) / C + 1e-6).astype(int), np.floor((mo[1] + s * P[:, 0] + c * P[:, 1]) / C + 1e-6).astype(int)))
    p = comp(mo, at(OB, OBt, st)); d = math.hypot(BC[0] - p[0], BC[1] - p[1]); b = math.atan2(BC[1] - p[1], BC[0] - p[0]) - p[2]; b = math.degrees(math.atan2(math.sin(b), math.cos(b)))
    seen = d <= 1.4 and abs(b) <= 43; mem = (mo[0] + c * bo[0] - s * bo[1], mo[1] + s * bo[0] + c * bo[1])
    for q in Q: rows[q].append((tt, q in cells, seen, d, b, mem))
print('bag %s · 조각 %d · 출발 기억 기준 t 1.1 s' % (Path(bag).name, len(SL)))
for q in Q:
    R = rows[q]; print('칸 (%.2f, %.2f): 장애물이었던 구간' % (q[0] * C, q[1] * C)); seg = None
    for i, (tt, on, seen, d, b, mem) in enumerate(R + [(1e9, False, False, 0, 0, (0, 0))]):
        if on and seg is None: seg = [tt, tt, 0, 0, d, b, mem]
        if on and seg is not None and tt - seg[1] <= 0.5: seg[1] = tt; seg[2] += 1; seg[3] += seen
        elif seg is not None and (not on or tt - seg[1] > 0.5):
            print('   t %6.1f ~ %6.1f s · 조각 %3d · 그중 상자 보임 %3d · 시작 때 상자 거리 %.2f m 방위 %+4.0f° · 출발 기억이 옮겨 갔을 자리 (%.3f, %.3f)' % (seg[0], seg[1], seg[2], seg[3], seg[4], seg[5], seg[6][0], seg[6][1]))
            seg = [tt, tt, 1, seen, d, b, mem] if on and tt < 1e8 else None
