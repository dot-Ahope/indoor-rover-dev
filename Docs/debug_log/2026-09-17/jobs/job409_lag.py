#!/usr/bin/env python3
"""명령 ω → 실제 yaw rate 지연·이득 (mp9·mp10·mp11): /cmd_vel ω 와 /odometry/filtered ω(카메라 자이로 융합) 를 20 ms 격자로 맞춘 뒤
   교차상관 최대가 되는 지연, 그 지연에서의 이득(최소제곱 기울기), 휠 목표(/rover/status tgt)→휠 측정(v) 지연도 함께.
   주행 구간(|v| > 0.03)만."""
import sys, math, re
import numpy as np
import rosbag2_py
from rclpy.serialization import deserialize_message
from rosidl_runtime_py.utilities import get_message
def load(bag, G):
    r = rosbag2_py.SequentialReader(); r.open(rosbag2_py.StorageOptions(uri=bag, storage_id='sqlite3'), rosbag2_py.ConverterOptions('', ''))
    ty = {t.name: t.type for t in r.get_all_topics_and_types()}; C, O, S, W = [], [], [], []
    while r.has_next():
        tp, d, ts = r.read_next(); t = ts * 1e-9 - G
        if tp == '/cmd_vel': m = deserialize_message(d, get_message(ty[tp])); C.append((t, m.linear.x, m.angular.z))
        elif tp == '/odometry/filtered': m = deserialize_message(d, get_message(ty[tp])); O.append((t, m.twist.twist.linear.x, m.twist.twist.angular.z))
        elif tp == '/wheel_odom': m = deserialize_message(d, get_message(ty[tp])); W.append((t, m.twist.twist.linear.x, m.twist.twist.angular.z))
    return C, O, W
def grid(seq, g, i):
    ts = np.array([s[0] for s in seq]); vs = np.array([s[i] for s in seq]); return np.interp(g, ts, vs)
for k in range(1, len(sys.argv), 2):
    bag, G = sys.argv[k], float(sys.argv[k + 1]); C, O, W = load(bag, G)
    tend = max(c[0] for c in C if abs(c[1]) > 0.02); g = np.arange(1.0, tend, 0.02)
    wc = grid(C, g, 2); vc = grid(C, g, 1); wo = grid(O, g, 2); ww = grid(W, g, 2)
    m = np.abs(vc) > 0.03
    def lagfit(a, b, name):
        a0 = a - a[m].mean(); best = None
        for L in range(0, 26):          # 0~0.50 s
            bb = np.roll(b, -L); mm = m.copy(); mm[len(mm) - L:] = False
            c = np.corrcoef(a0[mm], bb[mm])[0, 1]
            if best is None or c > best[1]: best = (L, c)
        L, c = best; bb = np.roll(b, -L); mm = m.copy(); mm[len(mm) - L:] = False
        gain = np.dot(a[mm], bb[mm]) / max(np.dot(a[mm], a[mm]), 1e-9)
        return '%s 지연 %.2f s (상관 %.2f, 이득 %.2f)' % (name, L * 0.02, c, gain)
    print('%s: %s | %s' % (bag.split('_')[-1], lagfit(wc, wo, '명령ω→EKF ω'), lagfit(wc, ww, '명령ω→휠오도 ω')))
