#!/usr/bin/env python3
"""anal_grid_phase — nvblox 거리 지도 조각과 로컬 코스트맵의 격자 원점이 0.05 m 칸에 대해 어디에 놓였는지(위상)를 시간순으로. (2026-10-15 §12, 오늘만)
  왜: 멈춘 칸이 카메라 원본(조각)에선 98 % 점유인데 로컬 코스트맵에선 약 30 % 빠짐 → 두 5 cm 격자를 옮겨 담는 과정(재표본)의 어긋남이 깜빡임 · 한 칸 과장을 만드는지.
  출력: 1 s 마다 조각 원점 x · y 의 (원점 mod 0.05), 코스트맵 원점의 (mod 0.05), 둘의 차(위상차, m). 위상차가 0 이 아니고 · 시간에 따라 바뀌면 칸 경계가 어긋남.
  인자: bag 시작HH:MM:SS 끝HH:MM:SS"""
import sys, time
from pathlib import Path
import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore, get_types_from_msg
ts_ = get_typestore(Stores.ROS2_HUMBLE)
ts_.register(get_types_from_msg('std_msgs/Header header\nfloat32 resolution\nuint32 width\nuint32 height\ngeometry_msgs/Point origin\nfloat32 unknown_value\nfloat32[] data\n', 'nvblox_msgs/msg/DistanceMapSlice'))
bag, h0, h1 = sys.argv[1:4]; sl = lc = None; last = 0; P = []
ph = lambda v: ((v % 0.05) + 0.05) % 0.05
with AnyReader([Path(bag)], default_typestore=ts_) as rd:
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/nvblox_node/static_map_slice', '/local_costmap/costmap')]):
        ts = t / 1e9; h = time.strftime('%H:%M:%S', time.localtime(ts)); m = rd.deserialize(raw, c.msgtype)
        if c.topic == '/local_costmap/costmap': lc = m
        else: sl = m
        if not (h0 <= h <= h1) or sl is None or lc is None or ts - last < 1.0: continue
        last = ts
        sx, sy = ph(sl.origin.x), ph(sl.origin.y); cx, cy = ph(lc.info.origin.position.x), ph(lc.info.origin.position.y)
        P.append((sx, sy, cx, cy))
        print('%s 조각 원점 (%.4f, %.4f) 위상 (%.4f, %.4f) · 코스트맵 원점 (%.4f, %.4f) 위상 (%.4f, %.4f) · 위상차 (%+.4f, %+.4f) · 조각 해상도 %.3f 프레임 %s' % (
            h, sl.origin.x, sl.origin.y, sx, sy, lc.info.origin.position.x, lc.info.origin.position.y, cx, cy, (sx - cx + 0.025) % 0.05 - 0.025, (sy - cy + 0.025) % 0.05 - 0.025, sl.resolution, sl.header.frame_id))
P = np.array(P); d = lambda a, b: (a - b + 0.025) % 0.05 - 0.025
print('위상차 x: 최소 %+.4f 최대 %+.4f · y: 최소 %+.4f 최대 %+.4f (m)' % (d(P[:, 0], P[:, 2]).min(), d(P[:, 0], P[:, 2]).max(), d(P[:, 1], P[:, 3]).min(), d(P[:, 1], P[:, 3]).max()))
