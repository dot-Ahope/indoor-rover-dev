#!/usr/bin/env python3
"""anal_rec_effect — 깊이 기록이 nvblox 에 영향을 줬나(2026-10-22 §7, PC): 출발 뒤 T 초 동안 nvblox 조각 · 로컬 코스트맵 주기, 조각 지연(bag 수신 − header.stamp) 분포.
  왜: 사용자 — f2dr1 에서 막은 칸 자리에 "아무것도 없다. bag 기록이 영향을 끼친 것 아닌지". 기록기가 깊이를 더 구독하면 카메라 발행 · nvblox 수신이 늦거나 빠질 수 있다.
  인자: T bag들"""
import sys
from pathlib import Path
import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore, get_types_from_msg
TS = get_typestore(Stores.ROS2_HUMBLE)
TS.register(get_types_from_msg('std_msgs/Header header\nfloat32 resolution\nuint32 width\nuint32 height\ngeometry_msgs/Point origin\nfloat32 unknown_value\nfloat32[] data\n', 'nvblox_msgs/msg/DistanceMapSlice'))
T = float(sys.argv[1])
for bag in sys.argv[2:]:
    R = {}
    with AnyReader([Path(bag)], default_typestore=TS) as rd:
        t0 = rd.start_time * 1e-9
        want = ('/nvblox_node/static_map_slice', '/local_costmap/costmap', '/camera/camera/depth/image_rect_raw')
        for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in want]):
            tt = t * 1e-9 - t0
            if tt > T: continue
            m = rd.deserialize(raw, c.msgtype); st = m.header.stamp.sec + m.header.stamp.nanosec * 1e-9
            R.setdefault(c.topic, []).append((tt, t * 1e-9 - st))
    print('bag %s · 처음 %.0f s' % (Path(bag).name, T))
    for k, v in R.items():
        a = np.array(v); gap = np.diff(a[:, 0]) if len(a) > 1 else np.array([0])
        print('  %-40s %4d 개 %.2f Hz · 최대 간격 %.2f s · 지연 중앙 %.3f s p95 %.3f 최대 %.3f' % (k, len(a), len(a) / T, gap.max(), np.median(a[:, 1]), np.percentile(a[:, 1], 95), a[:, 1].max()))
