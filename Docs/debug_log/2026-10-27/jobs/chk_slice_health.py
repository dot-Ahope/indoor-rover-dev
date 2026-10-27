#!/usr/bin/env python3
"""chk_slice_health — §19 nvblox 슬라이스가 계속 갱신됐나 (2026-10-27, PC). 2 s 마다: 슬라이스 수 · stamp 지연 · 원점 · 크기 ·
  장애(≤0) 칸 수 · 직전 2 s 대비 바뀐 칸 비율(거리값 |Δ| > 0.02, 겹치는 영역) · 로버 위치(map). 인자: bag폴더 시작 끝"""
import sys, time, math
import numpy as np
from pathlib import Path
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore, get_types_from_msg
ts_ = get_typestore(Stores.ROS2_HUMBLE)
ts_.register(get_types_from_msg('std_msgs/Header header\nfloat32 resolution\nuint32 width\nuint32 height\ngeometry_msgs/Point origin\nfloat32 unknown_value\nfloat32[] data\n', 'nvblox_msgs/msg/DistanceMapSlice'))
t0 = time.mktime(time.strptime('2026-10-27 ' + sys.argv[2], '%Y-%m-%d %H:%M:%S')); t1 = time.mktime(time.strptime('2026-10-27 ' + sys.argv[3], '%Y-%m-%d %H:%M:%S'))
hs = lambda t: time.strftime('%H:%M:%S', time.localtime(t))
SL = []; ob = []
with AnyReader([Path(sys.argv[1])], default_typestore=ts_) as rd:
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/nvblox_node/static_map_slice', '/tf')]):
        ts = t * 1e-9
        if not t0 <= ts <= t1: continue
        m = rd.deserialize(raw, c.msgtype)
        if c.topic == '/tf':
            for tr in m.transforms:
                if tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link': ob.append((ts, tr.transform.translation.x, tr.transform.translation.y))
            continue
        SL.append((ts, m.header.stamp.sec + m.header.stamp.nanosec * 1e-9, m.origin.x, m.origin.y, m.resolution, np.array(m.data, np.float32).reshape(m.height, m.width), m.unknown_value))
prev = None; k = 0
for w in np.arange(t0, t1, 2.0):
    B = [s for s in SL if w <= s[0] < w + 2]
    if not B: print('%s 슬라이스 0 개' % hs(w)); continue
    s = B[-1]; d = s[5]; obs = int(((d <= 0) & (d != s[6])).sum()); kn = int((d != s[6]).sum())
    ch = '-'
    if prev is not None and abs(prev[2] - s[2]) < 1e-6 and abs(prev[3] - s[3]) < 1e-6 and prev[5].shape == d.shape:
        v = (d != s[6]) & (prev[5] != prev[6]); ch = '%.3f' % (np.mean(np.abs(d[v] - prev[5][v]) > 0.02) if v.any() else 0)
    o = min(ob, key=lambda x: abs(x[0] - s[0])) if ob else (0, 0, 0)
    print('%s 슬라이스 %d 개 · 지연 %.2f s · 원점 (%.2f, %.2f) %dx%d · 아는 칸 %d · 장애 %d · 2 s 변화 %s · 로버 odom (%.2f, %.2f)' % (
        hs(w), len(B), s[0] - s[1], s[2], s[3], d.shape[1], d.shape[0], kn, obs, ch, o[1], o[2]))
    prev = s
