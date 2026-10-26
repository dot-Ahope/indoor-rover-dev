#!/usr/bin/env python3
"""chk_w3_turn — W3 출발 직후 '전진 명령 0 근처' 구간에 회전 명령 · 실제 회전(EKF)이 있었나 (2026-10-26 §13, PC). 인자: bag 시작HH:MM:SS.s 끝HH:MM:SS.s"""
import sys, time
from pathlib import Path
import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
C, E = [], []
with AnyReader([Path(sys.argv[1])], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/cmd_vel', '/odometry/filtered')]):
        m = rd.deserialize(raw, c.msgtype)
        (C if c.topic == '/cmd_vel' else E).append((t * 1e-9, m.linear.x if c.topic == '/cmd_vel' else m.twist.twist.linear.x, m.angular.z if c.topic == '/cmd_vel' else m.twist.twist.angular.z))
C, E = np.array(C), np.array(E); d0 = time.strftime('%Y-%m-%d ', time.localtime(C[0, 0]))
ep = lambda s: time.mktime(time.strptime(d0 + s[:8], '%Y-%m-%d %H:%M:%S')) + float(s[8:] or 0)
a, b = ep(sys.argv[2]), ep(sys.argv[3])
for t in np.arange(a, b, 0.5):
    mc = (C[:, 0] >= t) & (C[:, 0] < t + .5); me = (E[:, 0] >= t) & (E[:, 0] < t + .5)
    print('%s 명령 v %+.3f ω %+.3f | 실제 v %+.3f ω %+.3f' % (time.strftime('%H:%M:%S', time.localtime(t)) + '.%d' % int(t % 1 * 10), C[mc, 1].mean(), C[mc, 2].mean(), E[me, 1].mean(), E[me, 2].mean()))
