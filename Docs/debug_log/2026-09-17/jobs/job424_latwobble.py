#!/usr/bin/env python3
"""조향 흔들림이 위치에 주는 영향 (2026-09-17 §14): 통로 구간(odom x 0.6~1.45) odom->base_link 궤적에서
   1 s 창 2 차 다항식으로 매끈한 경로를 빼고 남은 횡 잔차(진행 방향 수직)와 yaw 잔차의 RMS·최대. 인자: BAG GOAL_EPOCH [...]
"""
import sys, math
import numpy as np
import rosbag2_py
from rclpy.serialization import deserialize_message
from tf2_msgs.msg import TFMessage


def yaw_of(q):
    return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))


a = sys.argv[1:]
for k in range(0, len(a), 2):
    bag, G = a[k], float(a[k + 1])
    r = rosbag2_py.SequentialReader(); r.open(rosbag2_py.StorageOptions(uri=bag, storage_id='sqlite3'), rosbag2_py.ConverterOptions('', ''))
    ob = []
    while r.has_next():
        topic, data, ts = r.read_next()
        if topic == '/tf':
            for tr in deserialize_message(data, TFMessage).transforms:
                if tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link':
                    ob.append((tr.header.stamp.sec + tr.header.stamp.nanosec * 1e-9 - G, tr.transform.translation.x, tr.transform.translation.y, yaw_of(tr.transform.rotation)))
    ob = np.array(sorted(ob)); tg = np.arange(0, ob[-1, 0], 0.05)
    X = np.interp(tg, ob[:, 0], ob[:, 1]); Y = np.interp(tg, ob[:, 0], ob[:, 2]); YW = np.interp(tg, ob[:, 0], np.unwrap(ob[:, 3]))
    idx = np.where((X > 0.6) & (X < 1.45))[0]
    lat, yr = [], []
    for i in idx:
        w = np.arange(max(i - 10, 0), min(i + 11, len(tg)))
        tt = tg[w] - tg[i]
        px, py, pw = np.polyfit(tt, X[w], 2), np.polyfit(tt, Y[w], 2), np.polyfit(tt, YW[w], 2)
        ex, ey = X[i] - px[-1], Y[i] - py[-1]; h = YW[i]
        lat.append(-ex * math.sin(h) + ey * math.cos(h)); yr.append(YW[i] - pw[-1])
    lat = np.array(lat); yr = np.array(yr)
    print('%s 통로 %d 점(20 Hz): 횡 잔차 RMS %.3f mm, 최대 %.3f mm | yaw 잔차 RMS %.3f°, 최대 %.3f°' % (
        bag.split('_')[-1], len(idx), 1000 * np.sqrt(np.mean(lat ** 2)), 1000 * np.abs(lat).max(), math.degrees(np.sqrt(np.mean(yr ** 2))), math.degrees(np.abs(yr).max())))
