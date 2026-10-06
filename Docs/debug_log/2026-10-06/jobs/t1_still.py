#!/usr/bin/env python3
"""10-06 §9 T1: 로버 정지 + 사람 이동 — SEC 초 동안 EKF B·A·rf2o 원 자세·게이트 판정 변화. 인자: SEC"""
import sys, time, math, rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from nav_msgs.msg import Odometry
SEC = float(sys.argv[1]); rclpy.init(); n = Node('t1_still'); P = {}; F = {}; V = {'n': 0, 'vmax': 0.0, 'over2': 0}
def sub(tp, k): n.create_subscription(Odometry, tp, lambda m: P.__setitem__(k, (m.pose.pose.position.x, m.pose.pose.position.y)), qos_profile_sensor_data)
sub('/odometry/filtered', 'B'); sub('/odometry/ekf_a', 'A'); sub('/odom_rf2o', 'R')
def cbg(m):
    v = math.hypot(m.twist.twist.linear.x, m.twist.twist.linear.y); V['n'] += 1; V['vmax'] = max(V['vmax'], v); V['over2'] += v > 0.02
n.create_subscription(Odometry, '/odom_rf2o/gated', cbg, qos_profile_sensor_data)
def cbr(m):
    v = math.hypot(m.twist.twist.linear.x, m.twist.twist.linear.y); F['vmax'] = max(F.get('vmax', 0.0), v); F['over2'] = F.get('over2', 0) + (v > 0.02); F['n'] = F.get('n', 0) + 1
n.create_subscription(Odometry, '/odom_rf2o', cbr, qos_profile_sensor_data)
t = time.time() + 3
while time.time() < t or len(P) < 3: rclpy.spin_once(n, timeout_sec=0.05)
P0 = dict(P); D = {k: 0.0 for k in P0}; t0 = time.time(); nxt = 10
while time.time() - t0 < SEC:
    rclpy.spin_once(n, timeout_sec=0.05)
    for k in P0: D[k] = max(D[k], math.hypot(P[k][0] - P0[k][0], P[k][1] - P0[k][1]))
    if time.time() - t0 > nxt: print('  %2.0f s  최대 이동 B %.3f · A %.3f · rf2o 원 %.3f m' % (nxt, D['B'], D['A'], D['R']), flush=True); nxt += 10
end = {k: math.hypot(P[k][0] - P0[k][0], P[k][1] - P0[k][1]) for k in P0}
print('T1 결과 %.0f s: 끝 이동 B %.3f · A %.3f · rf2o 원 %.3f m | 최대 B %.3f · A %.3f · rf2o 원 %.3f m' % (SEC, end['B'], end['A'], end['R'], D['B'], D['A'], D['R']))
print('  rf2o 원 속도: 표본 %d, 최대 %.3f m/s, 0.02 넘음 %d | 게이트 통과분: 표본 %d, 최대 %.3f m/s, 0.02 넘음 %d' % (F.get('n', 0), F.get('vmax', 0), F.get('over2', 0), V['n'], V['vmax'], V['over2']))
