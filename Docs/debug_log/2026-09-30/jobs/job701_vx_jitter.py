#!/usr/bin/env python3
"""09-30 §7.4 EKF 직진 속도 흔들림의 출처(v2): 전진 주행 전체(명령 v ≥ 0.075)에서 신호마다 1 s 이동평균을 뺀 **빠른 흔들림**의
   표준편차·주된 주파수를 원본 휠 vx(/wheel_odom 25 Hz)와 EKF vx(/odometry/filtered 30 Hz)로 비교.
   함께: 같은 시각 EKF vx − 휠 vx 차의 표준편차, 휠 ω·자이로 ω 의 빠른 흔들림(회전 쪽 참고). 인자: BAG"""
import sys
import numpy as np
import rosbag2_py
from rclpy.serialization import deserialize_message
from rosidl_runtime_py.utilities import get_message

r = rosbag2_py.SequentialReader(); r.open(rosbag2_py.StorageOptions(uri=sys.argv[1], storage_id='sqlite3'), rosbag2_py.ConverterOptions('cdr', 'cdr'))
types = {t.name: t.type for t in r.get_all_topics_and_types()}
S = {'/wheel_odom': [], '/odometry/filtered': [], '/cmd_vel': [], '/imu/data': []}
while r.has_next():
    tp, data, ts = r.read_next()
    if tp not in S: continue
    m = deserialize_message(data, get_message(types[tp])); t = ts * 1e-9
    if tp == '/cmd_vel': S[tp].append((t, m.linear.x, m.angular.z))
    elif tp == '/imu/data': S[tp].append((t, -m.angular_velocity.y, 0.0))
    else: S[tp].append((t, m.twist.twist.linear.x, m.twist.twist.angular.z))
S = {k: np.array(v) for k, v in S.items() if v}
C = S['/cmd_vel']; t0, t1 = C[0, 0], C[-1, 0]


def fwd_mask(t):
    k = np.clip(np.searchsorted(C[:, 0], t) - 1, 0, len(C) - 1); return (C[k, 1] >= 0.075) & (t - C[k, 0] < 0.5)


def hf(X, col):
    t, x = X[:, 0], X[:, col]; dt = np.median(np.diff(t)); n = max(3, int(round(1.0 / dt)))
    trend = np.convolve(x, np.ones(n) / n, mode='same'); y = x - trend; m = fwd_mask(t) & (t > t0 + 1) & (t < t1 - 1)
    sp = np.abs(np.fft.rfft(np.where(m, y, 0))); f = np.fft.rfftfreq(len(y), dt)
    return 1 / dt, y[m].std(), f[1 + np.argmax(sp[1:])], x[m].mean(), m.sum()


for name, key, col in (('원본 휠 vx', '/wheel_odom', 1), ('EKF vx', '/odometry/filtered', 1), ('원본 휠 ω', '/wheel_odom', 2), ('자이로 ω', '/imu/data', 1), ('EKF ω', '/odometry/filtered', 2)):
    if key not in S: print('%s: 토픽 없음' % name); continue
    hz, sd, fp, mu, n = hf(S[key], col)
    print('%-10s %5.1f Hz | 전진 구간 %4d 표본 평균 %+.4f | 빠른 흔들림 σ %.4f | 주된 주파수 %.2f Hz' % (name, hz, n, mu, sd, fp))
W, E = S['/wheel_odom'], S['/odometry/filtered']
wi = np.interp(E[:, 0], W[:, 0], W[:, 1]); m = fwd_mask(E[:, 0])
print('같은 시각 EKF vx − 휠 vx: 평균 %+.4f, σ %.4f m/s' % ((E[m, 1] - wi[m]).mean(), (E[m, 1] - wi[m]).std()))
gi = np.interp(E[:, 0], S['/imu/data'][:, 0], S['/imu/data'][:, 1]); wwi = np.interp(E[:, 0], W[:, 0], W[:, 2])
print('참고 회전: 휠 ω − 자이로 ω σ %.3f, EKF ω − 자이로 ω σ %.3f rad/s (전진 구간)' % ((wwi[m] - gi[m]).std(), (E[m, 2] - gi[m]).std()))
