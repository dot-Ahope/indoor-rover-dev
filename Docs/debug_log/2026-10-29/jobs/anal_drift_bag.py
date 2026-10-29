#!/usr/bin/env python3
"""anal_drift_bag — 정지 기록 bag 에서 방향 드리프트 원천 가르기 (10-29 §1 판정 ①~④, PC).
  구간(BIN s, 기본 300)마다:
    EKF odom→base_link yaw 변화 · map→odom yaw 변화
    ∫ 조건 IMU(/imu/data 광학 −y) · ∫ 원시 IMU(/camera/camera/imu 광학 −y) · ∫ 휠 wz · ∫ EKF twist wz  (° 단위)
    원시 − 조건 평균 = 그 구간에 컨디셔너가 뺀 바이어스(°/min)
  끝에 전체 합과 판정 ①②④ 숫자. 인자: bag폴더 [BIN]"""
import sys, math
import numpy as np
from pathlib import Path
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore

bag = Path(sys.argv[1]); BIN = float(sys.argv[2]) if len(sys.argv) > 2 else 300.0
yaw = lambda q: math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
OB, MO, IMU, RAW, WH, EK = [], [], [], [], [], []
with AnyReader([bag], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
    want = ('/tf', '/imu/data', '/camera/camera/imu', '/wheel_odom/conditioned', '/odometry/filtered')
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in want]):
        m = rd.deserialize(raw, c.msgtype)
        if c.topic == '/tf':
            for tr in m.transforms:
                ts = tr.header.stamp.sec + tr.header.stamp.nanosec * 1e-9
                if tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link': OB.append((ts, yaw(tr.transform.rotation)))
                elif tr.header.frame_id == 'map' and tr.child_frame_id == 'odom': MO.append((ts, yaw(tr.transform.rotation)))
            continue
        ts = m.header.stamp.sec + m.header.stamp.nanosec * 1e-9
        if c.topic == '/imu/data': IMU.append((ts, -m.angular_velocity.y))
        elif c.topic == '/camera/camera/imu': RAW.append((ts, -m.angular_velocity.y))
        elif c.topic == '/wheel_odom/conditioned': WH.append((ts, m.twist.twist.angular.z))
        else: EK.append((ts, m.twist.twist.angular.z))
A = {k: np.array(sorted(v)) for k, v in (('ob', OB), ('mo', MO), ('imu', IMU), ('raw', RAW), ('wh', WH), ('ek', EK))}
for k, v in A.items(): print('%s %d 개' % (k, len(v)), end=' · ')
print()
t0 = max(A['ob'][0, 0], A['imu'][0, 0]); t1 = min(A['ob'][-1, 0], A['imu'][-1, 0])
def dyaw(X, a, b):
    i, j = np.searchsorted(X[:, 0], a), min(np.searchsorted(X[:, 0], b), len(X) - 1)
    u = np.unwrap(X[i:j + 1, 1]); return math.degrees(u[-1] - u[0]) if len(u) > 1 else float('nan')
def integ(X, a, b):
    s = X[(X[:, 0] >= a) & (X[:, 0] < b)]
    if len(s) < 2: return float('nan'), float('nan')
    dt = np.diff(s[:, 0]); dt = np.minimum(dt, 0.2)   # 빠진 구간은 0.2 s 까지만 이어 붙임
    return math.degrees(float(np.sum(s[:-1, 1] * dt))), math.degrees(float(s[:, 1].mean())) * 60
print('구간 t s      | EKF Δ°  | map→odom Δ° | ∫조건IMU° | ∫원시IMU° | ∫휠° | ∫EKF wz° | 뺀 바이어스 °/min')
edges = list(np.arange(t0, t1, BIN)) + [t1]
for a, b in zip(edges[:-1], edges[1:]):
    ci, cm = integ(A['imu'], a, b); ri, rm = integ(A['raw'], a, b)
    print('%5.0f–%5.0f | %+7.3f | %+7.3f | %+8.3f | %+8.3f | %+5.2f | %+7.3f | %+.3f' % (
        a - t0, b - t0, dyaw(A['ob'], a, b), dyaw(A['mo'], a, b), ci, ri, integ(A['wh'], a, b)[0], integ(A['ek'], a, b)[0], rm - cm))
E, M = dyaw(A['ob'], t0, t1), dyaw(A['mo'], t0, t1); C = integ(A['imu'], t0, t1)[0]; R = integ(A['raw'], t0, t1)[0]
print('전체 %.0f s: EKF Δ %+.3f° (%+.3f °/min) · map→odom Δ %+.3f° · ∫조건IMU %+.3f° · ∫원시IMU %+.3f° · ∫휠 %+.3f° · ∫EKF wz %+.3f°' % (
    t1 - t0, E, E / (t1 - t0) * 60, M, C, R, integ(A['wh'], t0, t1)[0], integ(A['ek'], t0, t1)[0]))
print('판정 ① |EKF Δ| %.2f° (≥3 재현 · <1 안 됨) · ② ∫조건IMU/EKF Δ = %s · ④ |map→odom Δ| %.2f° (<0.5 = 안 고침)' % (
    abs(E), ('%.0f %%' % (C / E * 100)) if abs(E) > 0.05 else 'EKF Δ 너무 작아 비율 무의미', abs(M)))
