#!/usr/bin/env python3
"""EKF 상태 잡음 실측 (2026-09-17 §14): 컨트롤러가 받는 /odometry/filtered twist·odom->base_link 자세의 잡음.
   (1) 정지 구간(목표 전 −6~−0.5 s): ω·v 표준편차, yaw·x·y 표준편차 — 순수 센서/필터 잡음
   (2) 주행 통로 구간(odom x 0.6~1.45): 10 Hz 로 뽑은 yaw 의 2 차 차분 잔차 RMS(매끈한 운동 제거), ω 의 0.1 s 차분 RMS
   인자: BAG GOAL_EPOCH [...]
"""
import sys, math
import numpy as np
import rosbag2_py
from rclpy.serialization import deserialize_message
from nav_msgs.msg import Odometry
from tf2_msgs.msg import TFMessage


def yaw_of(q):
    return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))


a = sys.argv[1:]
for k in range(0, len(a), 2):
    bag, G = a[k], float(a[k + 1])
    r = rosbag2_py.SequentialReader(); r.open(rosbag2_py.StorageOptions(uri=bag, storage_id='sqlite3'), rosbag2_py.ConverterOptions('', ''))
    od, ob = [], []
    while r.has_next():
        topic, data, ts = r.read_next(); t = ts * 1e-9 - G
        if topic == '/odometry/filtered':
            m = deserialize_message(data, Odometry); od.append((t, m.twist.twist.linear.x, m.twist.twist.angular.z))
        elif topic == '/tf':
            for tr in deserialize_message(data, TFMessage).transforms:
                if tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link':
                    ob.append((tr.header.stamp.sec + tr.header.stamp.nanosec * 1e-9 - G, tr.transform.translation.x, tr.transform.translation.y, yaw_of(tr.transform.rotation)))
    od = np.array(sorted(od)); ob = np.array(sorted(ob))
    s0 = (od[:, 0] > -6) & (od[:, 0] < -0.5); p0 = (ob[:, 0] > -6) & (ob[:, 0] < -0.5)
    name = bag.split('_')[-1]
    print('%s 정지(%.1f s, odom %d·tf %d): ω std %.4f rad/s, v std %.4f m/s | yaw std %.3f°, x std %.4f, y std %.4f m' % (
        name, od[s0, 0].ptp() if s0.any() else 0, s0.sum(), p0.sum(), od[s0, 2].std() if s0.any() else float('nan'), od[s0, 1].std() if s0.any() else float('nan'),
        math.degrees(np.unwrap(ob[p0, 3]).std()) if p0.any() else float('nan'), ob[p0, 1].std() if p0.any() else float('nan'), ob[p0, 2].std() if p0.any() else float('nan')))
    # 통로 구간 10 Hz 격자
    tg = np.arange(0, ob[-1, 0], 0.1)
    X = np.interp(tg, ob[:, 0], ob[:, 1]); Y = np.interp(tg, ob[:, 0], ob[:, 2]); YW = np.interp(tg, ob[:, 0], np.unwrap(ob[:, 3]))
    W = np.interp(tg, od[:, 0], od[:, 2])
    m = (X > 0.6) & (X < 1.45)
    d2 = YW[2:] - 2 * YW[1:-1] + YW[:-2]; mm = m[1:-1]
    dw = np.diff(W); mw = m[1:]
    lat = -(np.diff(X)) * np.sin(YW[1:]) + np.diff(Y) * np.cos(YW[1:]); ml = m[1:]
    print('%s 통로(10 Hz %d 점): yaw 2차차분 RMS %.3f°, ω 0.1 s 차분 RMS %.4f rad/s, 차체 횡방향 이동/주기 RMS %.4f m' % (
        name, m.sum(), math.degrees(np.sqrt(np.mean(d2[mm] ** 2))), np.sqrt(np.mean(dw[mw] ** 2)), np.sqrt(np.mean(lat[ml] ** 2))))
