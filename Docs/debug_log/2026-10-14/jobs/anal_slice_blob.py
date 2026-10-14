#!/usr/bin/env python3
"""anal_slice_blob — nvblox 거리 지도 조각(/nvblox_node/static_map_slice)에서 상자 끝 덩어리 구역이 시간에 따라 어땠는지. (2026-10-14 §24, 오늘만)
  왜: f2u2 16:30:06.6 의 계획기 경로만 전역 내접 칸을 지났다(앞뒤 경로·f2r1 은 정상). 그 순간 nvblox 층이 잠깐 비어 계획기가 덩어리 없는 지도를 봤는지 확인.
  출력: 조각마다 — 구역(지도 좌표) 칸 수, 아는 칸 수, 최소 거리, 0.05 m 이하(장애물로 보는) 칸 수.
  인자: bag 시작HH:MM:SS 끝HH:MM:SS [x0 x1 y0 y1 = 0.9 1.35 -0.2 0.12]"""
import sys, time, math
from pathlib import Path
import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore, get_types_from_msg
ts_ = get_typestore(Stores.ROS2_HUMBLE)
ts_.register(get_types_from_msg('std_msgs/Header header\nfloat32 resolution\nuint32 width\nuint32 height\ngeometry_msgs/Point origin\nfloat32 unknown_value\nfloat32[] data\n', 'nvblox_msgs/msg/DistanceMapSlice'))
bag, h0, h1 = sys.argv[1:4]; X0, X1, Y0, Y1 = [float(v) for v in sys.argv[4:8]] if len(sys.argv) > 7 else (0.9, 1.35, -0.2, 0.12)
yq = lambda q: math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
mo = None
with AnyReader([Path(bag)], default_typestore=ts_) as rd:
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/tf', '/nvblox_node/static_map_slice')]):
        h = time.strftime('%H:%M:%S', time.localtime(t / 1e9)); m = rd.deserialize(raw, c.msgtype)
        if c.topic == '/tf':
            for tr in m.transforms:
                if tr.child_frame_id == 'odom' and tr.header.frame_id == 'map': mo = (tr.transform.translation.x, tr.transform.translation.y, yq(tr.transform.rotation))
            continue
        if not (h0 <= h <= h1) or mo is None: continue
        d = np.array(m.data, np.float32).reshape(m.height, m.width); iy, ix = np.indices(d.shape)
        sx = m.origin.x + (ix + 0.5) * m.resolution; sy = m.origin.y + (iy + 0.5) * m.resolution
        if m.header.frame_id == 'map': mx, my = sx, sy
        else: c_, s_ = math.cos(mo[2]), math.sin(mo[2]); mx = mo[0] + c_ * sx - s_ * sy; my = mo[1] + s_ * sx + c_ * sy
        reg = (mx > X0) & (mx < X1) & (my > Y0) & (my < Y1); kn = reg & (d != m.unknown_value)
        print('%s.%d [%s] 구역 칸 %d · 아는 칸 %d · 최소 거리 %.3f m · 0.05 m 이하 %d' % (h, int(t / 1e8) % 10, m.header.frame_id, reg.sum(), kn.sum(), d[kn].min() if kn.any() else float('nan'), (kn & (d <= 0.05)).sum()))
