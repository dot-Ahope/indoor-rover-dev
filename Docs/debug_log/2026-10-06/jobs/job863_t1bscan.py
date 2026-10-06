#!/usr/bin/env python3
"""10-06 §9 T1 확인: 사람 움직임이 라이다에 실제로 보였나 — 2 m 안 점 중 첫 스캔과 5 cm 넘게 다른 점 수(스캔별)·각도 범위"""
import math, numpy as np, rosbag2_py
from rclpy.serialization import deserialize_message
from sensor_msgs.msg import LaserScan
r = rosbag2_py.SequentialReader(); r.open(rosbag2_py.StorageOptions(uri='/tmp/bag_t1b', storage_id='sqlite3'), rosbag2_py.ConverterOptions('cdr', 'cdr'))
R0 = None; out = []; t0 = None
while r.has_next():
    tp, d, ts = r.read_next()
    if tp != '/scan': continue
    m = deserialize_message(d, LaserScan); rr = np.array(m.ranges, dtype=float); rr[~np.isfinite(rr)] = 0
    if t0 is None: t0 = ts
    if R0 is None: R0 = rr.copy(); ang = m.angle_min + m.angle_increment * np.arange(len(rr)) + math.pi - 0.04677; continue
    near = ((rr > 0.2) & (rr < 2.0)) | ((R0 > 0.2) & (R0 < 2.0)); ch = near & (np.abs(rr - R0) > 0.05)
    out.append(((ts - t0) * 1e-9, ch.sum(), np.degrees((ang[ch] + np.pi) % (2 * np.pi) - np.pi) if ch.any() else np.array([])))
a = np.array([o[1] for o in out]); print('스캔 %d 개, 2 m 안 바뀐 점: 중앙 %d · 90%% %d · 최대 %d' % (len(a), np.median(a), np.percentile(a, 90), a.max()))
big = [o for o in out if o[1] > 20]
if big: allang = np.concatenate([o[2] for o in big]); print('바뀐 점 20 개 넘는 스캔 %d 개(%.0f~%.0f s), 차체 기준 각도 %.0f~%.0f° (0 = 앞)' % (len(big), big[0][0], big[-1][0], np.percentile(allang, 5), np.percentile(allang, 95)))
