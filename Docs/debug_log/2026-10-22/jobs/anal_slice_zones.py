#!/usr/bin/env python3
"""anal_slice_zones — nvblox 조각(실시간 또는 재생)으로 유령 · 상자 지표(2026-10-22 §9, PC). 기준 §5.
  유령: 영역마다 시간 창 안에 한 번이라도 거리 ≤ 0(장애물)이 된 지도 칸(0.05 m) 수 — 맨바닥 영역엔 실물이 없음(사용자 확인 10-21 · 10-22).
  상자: 상자 영역 칸 수의 시간 창 중앙 · 최대. 시각은 조각 header.stamp − 주행 bag 시작(재생은 sim time = bag 시각이라 같은 축).
  인자: 주행bag 이름=조각bag ...  (조각bag 이 'live' 면 주행 bag 안의 실시간 조각)"""
import sys, math, bisect
from pathlib import Path
import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore, get_types_from_msg
TS = get_typestore(Stores.ROS2_HUMBLE)
TS.register(get_types_from_msg('std_msgs/Header header\nfloat32 resolution\nuint32 width\nuint32 height\ngeometry_msgs/Point origin\nfloat32 unknown_value\nfloat32[] data\n', 'nvblox_msgs/msg/DistanceMapSlice'))
ZONES = {'A 맨바닥': (1.45, 2.65, -0.35, 0.45, 10, 60), 'B 문': (2.00, 2.60, -0.85, -0.45, 10, 60), '북쪽': (1.10, 2.20, 0.45, 1.15, 0, 42)}
BOXR, BT0 = (1.15, 1.35, -0.20, 0.05), None
yq = lambda q: math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
drive = sys.argv[1]; MO = []
with AnyReader([Path(drive)], default_typestore=TS) as rd:
    T0 = rd.start_time * 1e-9
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic == '/tf']):
        for tr in rd.deserialize(raw, c.msgtype).transforms:
            if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom':
                MO.append((tr.header.stamp.sec + tr.header.stamp.nanosec * 1e-9, (tr.transform.translation.x, tr.transform.translation.y, yq(tr.transform.rotation))))
MO.sort(); MOt = [m[0] for m in MO]
BT0 = float(sys.argv[2]) if len(sys.argv) > 2 and '=' not in sys.argv[2] else 2.88   # 상자 t0(§8.1 anal_box_detect)
print('주행 bag %s · 상자 t0 %.2f s · 지표: 영역별 한 번이라도 장애물 된 칸 수, 상자 영역 칸 수(t0~t0+10 s) 중앙 · 최대' % (Path(drive).name, BT0))
for arg in [a for a in sys.argv[2:] if '=' in a]:
    nm, sb = arg.split('='); src = drive if sb == 'live' else sb
    ever = {k: set() for k in ZONES}; box = []; n = 0
    with AnyReader([Path(src)], default_typestore=TS) as rd:
        for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic == '/nvblox_node/static_map_slice']):
            m = rd.deserialize(raw, c.msgtype); st = m.header.stamp.sec + m.header.stamp.nanosec * 1e-9; tt = st - T0; n += 1
            mo = (0.0, 0.0, 0.0) if m.header.frame_id == 'map' else MO[max(bisect.bisect_right(MOt, st) - 1, 0)][1]
            d = np.array(m.data, np.float32).reshape(m.height, m.width); iy, ix = np.nonzero((d <= 0) & (d != m.unknown_value)); r = m.resolution
            lx = m.origin.x + (ix + 0.5) * r; ly = m.origin.y + (iy + 0.5) * r
            gx = mo[0] + math.cos(mo[2]) * lx - math.sin(mo[2]) * ly; gy = mo[1] + math.sin(mo[2]) * lx + math.cos(mo[2]) * ly
            for k, (x0, x1, y0, y1, ta, tb) in ZONES.items():
                if ta <= tt <= tb:
                    s = (gx >= x0) & (gx <= x1) & (gy >= y0) & (gy <= y1)
                    ever[k].update(zip(np.floor(gx[s] / 0.05).astype(int), np.floor(gy[s] / 0.05).astype(int)))
            if BT0 <= tt <= BT0 + 10:
                x0, x1, y0, y1 = BOXR; box.append(int(np.sum((gx >= x0) & (gx <= x1) & (gy >= y0) & (gy <= y1))))
    print('  %-8s 조각 %4d · %s · 상자 중앙 %s 최대 %s (조각 %d)' % (nm, n, ' · '.join('%s %d' % (k, len(v)) for k, v in ever.items()),
          int(np.median(box)) if box else '-', max(box) if box else '-', len(box)))
