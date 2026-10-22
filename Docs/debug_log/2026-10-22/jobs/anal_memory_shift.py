#!/usr/bin/env python3
"""anal_memory_shift — 출발 때 본 상자를 nvblox 가 odom 좌표로 기억한다고 할 때, 그 뒤 map→odom 보정만으로 지도에서 얼마나 옮겨 보이는지(2026-10-22 §11, PC).
  계산: 상자 중심(지도) → 기준 시각 map→odom 역변환으로 odom 점 → 각 시각 map→odom 으로 다시 지도 점. 차이 = 기억이 지도에서 밀린 양.
  인자: 주행bag 기준시각s 시각들s(쉼표)"""
import sys, math, bisect
from pathlib import Path
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
bag, tr0 = sys.argv[1], float(sys.argv[2]); TQ = [float(v) for v in sys.argv[3].split(',')]
BC = ((1.151 + 1.261) / 2, (-0.20 - 0.02) / 2)
yq = lambda q: math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
MO = []
with AnyReader([Path(bag)], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
    T0 = rd.start_time * 1e-9
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic == '/tf']):
        for tr in rd.deserialize(raw, c.msgtype).transforms:
            if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom':
                MO.append((tr.header.stamp.sec + tr.header.stamp.nanosec * 1e-9 - T0, (tr.transform.translation.x, tr.transform.translation.y, yq(tr.transform.rotation))))
MO.sort(); MOt = [q[0] for q in MO]; at = lambda t: MO[max(bisect.bisect_right(MOt, t) - 1, 0)][1]
a = at(tr0); dx, dy = BC[0] - a[0], BC[1] - a[1]; c, s = math.cos(-a[2]), math.sin(-a[2]); po = (c * dx - s * dy, s * dx + c * dy)
print('bag %s · 상자 중심 (%.3f, %.3f) · 기준 t %.1f s map→odom (%.3f, %.3f, %.2f°)' % (Path(bag).name, *BC, tr0, a[0], a[1], math.degrees(a[2])))
for t in TQ:
    b = at(t); c, s = math.cos(b[2]), math.sin(b[2]); x, y = b[0] + c * po[0] - s * po[1], b[1] + s * po[0] + c * po[1]
    print('  t %6.1f s · map→odom (%.3f, %.3f, %+.2f°) · 기억된 상자 중심 → (%.3f, %.3f) · 밀림 Δx %+.3f Δy %+.3f (%.3f m)' % (t, b[0], b[1], math.degrees(b[2]), x, y, x - BC[0], y - BC[1], math.hypot(x - BC[0], y - BC[1])))
