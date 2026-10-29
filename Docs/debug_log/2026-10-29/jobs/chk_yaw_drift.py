#!/usr/bin/env python3
"""chk_yaw_drift — 정지 중 방향 드리프트 원천 측정 (2026-10-29, Jetson, 로버 안 움직임).
  인자: 창 길이 s(기본 60). 그 창 동안:
  · TF odom→base_link yaw · map→odom yaw 처음/끝 → 창 안 yaw 변화율(°/min)
  · 각 yaw rate 원천의 평균 · 표준편차: 카메라 원시 IMU(/camera/camera/imu 광학 -y) · 컨디셔너 출력(/imu/data 광학 -y)
    · 휠(/wheel_odom/conditioned twist.angular.z) · cuVSLAM(/vslam/odom twist) · EKF(/odometry/filtered twist.angular.z)
  · 수신 개수(빠진 원천 확인)"""
import sys, math, time
import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data, QoSProfile, ReliabilityPolicy
from sensor_msgs.msg import Imu
from nav_msgs.msg import Odometry
from tf2_ros import Buffer, TransformListener

W = float(sys.argv[1]) if len(sys.argv) > 1 else 60.0
yaw = lambda q: math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
rclpy.init(); n = Node('chk_yaw_drift'); buf = Buffer(); TransformListener(buf, n)
D = {k: [] for k in ('cam_raw', 'imu_data', 'wheel', 'vslam_wz', 'vslam_vx', 'ekf_wz', 'ekf_vx')}
be = QoSProfile(depth=50, reliability=ReliabilityPolicy.BEST_EFFORT)
n.create_subscription(Imu, '/camera/camera/imu', lambda m: D['cam_raw'].append(-m.angular_velocity.y), qos_profile_sensor_data)
n.create_subscription(Imu, '/imu/data', lambda m: D['imu_data'].append(-m.angular_velocity.y), be)
n.create_subscription(Odometry, '/wheel_odom/conditioned', lambda m: D['wheel'].append(m.twist.twist.angular.z), be)
n.create_subscription(Odometry, '/vslam/odom', lambda m: (D['vslam_wz'].append(m.twist.twist.angular.z), D['vslam_vx'].append(m.twist.twist.linear.x)), be)
n.create_subscription(Odometry, '/odometry/filtered', lambda m: (D['ekf_wz'].append(m.twist.twist.angular.z), D['ekf_vx'].append(m.twist.twist.linear.x)), be)

def tfyaw(p, c):
    try:
        t = buf.lookup_transform(p, c, rclpy.time.Time()); return yaw(t.transform.rotation), t.header.stamp.sec + t.header.stamp.nanosec * 1e-9
    except Exception as e:
        return None, str(e)[:60]

t_end = time.time() + 3
while time.time() < t_end: rclpy.spin_once(n, timeout_sec=0.1)
for k in D: D[k].clear()
a0 = tfyaw('odom', 'base_link'); m0 = tfyaw('map', 'odom'); w0 = time.time()
while time.time() < w0 + W: rclpy.spin_once(n, timeout_sec=0.05)
a1 = tfyaw('odom', 'base_link'); m1 = tfyaw('map', 'odom'); dt = time.time() - w0
print('== chk_yaw_drift  %s  창 %.1f s' % (time.strftime('%F %T'), dt))
for nm, x0, x1 in (('odom→base_link', a0, a1), ('map→odom', m0, m1)):
    if x0[0] is None or x1[0] is None: print('  %s: TF 없음 %s %s' % (nm, x0[1], x1[1])); continue
    d = math.degrees(math.atan2(math.sin(x1[0] - x0[0]), math.cos(x1[0] - x0[0])))
    print('  %-15s yaw %+8.3f° → %+8.3f°  변화 %+7.3f° = %+6.3f °/min  (stamp 끝 %.1f s 전)' % (nm, math.degrees(x0[0]), math.degrees(x1[0]), d, d / dt * 60, time.time() - x1[1]))
print('  원천            개수    평균 rad/s      = °/min    표준편차')
for k, v in D.items():
    if not v: print('  %-14s %6d   (수신 없음)' % (k, 0)); continue
    a = np.array(v); u = '' if k.endswith('_vx') else '%+8.3f' % (a.mean() * 57.29578 * 60)
    print('  %-14s %6d   %+.6f   %8s   %.5f' % (k, len(a), a.mean(), u, a.std()))
n.destroy_node(); rclpy.shutdown()
