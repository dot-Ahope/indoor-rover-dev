#!/usr/bin/env python3
"""chk_mapodom_window — §21 컨트롤러 TF 중단 순간 앞뒤의 map→odom(/tf) 수신 시각 · stamp (2026-10-27, PC). 인자: bag폴더 epoch초…(중단 로그 시각)"""
import sys, time
from pathlib import Path
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
W = [float(x) for x in sys.argv[2:]]; R = []
with AnyReader([Path(sys.argv[1])], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic == '/tf']):
        ts = t * 1e-9
        if not any(w - 1.6 <= ts <= w + 0.3 for w in W): continue
        for tr in rd.deserialize(raw, c.msgtype).transforms:
            if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom': R.append((ts, tr.header.stamp.sec + tr.header.stamp.nanosec * 1e-9))
for w in W:
    print('== 중단 로그 %.3f (%s)' % (w, time.strftime('%H:%M:%S', time.localtime(w))))
    for ts, st in R:
        if w - 1.6 <= ts <= w + 0.3: print('  수신 %+.3f s · stamp %+.3f s (수신 기준 stamp %+.3f)' % (ts - w, st - w, st - ts))
