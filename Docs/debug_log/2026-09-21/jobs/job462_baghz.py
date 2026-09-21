#!/usr/bin/env python3
"""S5 기준선: bag 에서 토픽별 실측 발행 주기 (2026-09-21 §7). 인자: BAG [BAG ...]
  주행 구간(첫 /cmd_vel |v|>0.01 ~ 마지막) 안에서 수신 시각 간격의 중앙·최대, 메시지 수 → Hz. 코스트맵·경로·센서·odom.
"""
import sys
import numpy as np
import rosbag2_py
from rclpy.serialization import deserialize_message
from geometry_msgs.msg import Twist
WANT = ['/local_costmap/costmap', '/global_costmap/costmap', '/plan', '/plan_smoothed', '/cmd_vel', '/odometry/filtered', '/wheel_odom', '/scan', '/tf', '/map']
for bag in sys.argv[1:]:
    r = rosbag2_py.SequentialReader(); r.open(rosbag2_py.StorageOptions(uri=bag, storage_id='sqlite3'), rosbag2_py.ConverterOptions('', ''))
    T = {k: [] for k in WANT}; cmd = []
    while r.has_next():
        topic, data, ts = r.read_next(); t = ts * 1e-9
        if topic in T: T[topic].append(t)
        if topic == '/cmd_vel':
            m = deserialize_message(data, Twist); cmd.append((t, abs(m.linear.x) > 0.01 or abs(m.angular.z) > 0.02))
    mv = [t for t, on in cmd if on]; t0, t1 = (min(mv), max(mv)) if mv else (cmd[0][0], cmd[-1][0])
    print('==== %s: 주행 구간 %.1f s' % (bag.split('/')[-1], t1 - t0))
    for k in WANT:
        a = np.array([t for t in T[k] if t0 <= t <= t1])
        if a.size < 2: print('  %-24s 없음' % k); continue
        d = np.diff(np.sort(a))
        print('  %-24s %4d 개  %.2f Hz | 간격 중앙 %.3f 최대 %.3f s' % (k, a.size, (a.size - 1) / (a[-1] - a[0]), np.median(d), d.max()))
