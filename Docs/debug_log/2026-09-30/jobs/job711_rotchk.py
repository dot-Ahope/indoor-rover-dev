#!/usr/bin/env python3
"""09-30 §12: 회전 중 지도 위 로버가 안 도는 현상 — 15 s 동안 1 s 간격으로
   odom→base_link yaw(EKF), map→odom yaw(SLAM 보정), map→base_link yaw, 그리고 각 입력의 회전 속도·수신 주기.
   판정: 로버를 돌리는데 odom→base_link yaw 가 안 변하면 EKF 쪽(입력 끊김), odom 은 변하는데 map 이 늦으면 TF/SLAM 쪽."""
import time, math
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from nav_msgs.msg import Odometry
from sensor_msgs.msg import Imu
from tf2_ros import Buffer, TransformListener


def yaw(q): return math.degrees(math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z)))


rclpy.init(); n = Node('rot_chk'); tb = Buffer(); TransformListener(tb, n)
cnt = {'/wheel_odom': 0, '/wheel_odom/conditioned': 0, '/imu/data': 0, '/odometry/filtered': 0}
last = {}
def mk(k):
    def cb(m):
        cnt[k] += 1
        last[k] = (m.twist.twist.angular.z if hasattr(m, 'twist') else m.angular_velocity.y * -1)
    return cb
n.create_subscription(Odometry, '/wheel_odom', mk('/wheel_odom'), qos_profile_sensor_data)
n.create_subscription(Odometry, '/wheel_odom/conditioned', mk('/wheel_odom/conditioned'), qos_profile_sensor_data)
n.create_subscription(Imu, '/imu/data', mk('/imu/data'), qos_profile_sensor_data)
n.create_subscription(Odometry, '/odometry/filtered', mk('/odometry/filtered'), 20)
t0 = time.time(); tick = 1.0
print(' t   odom→base yaw  map→odom yaw  map→base yaw | ω 휠 / 휠(컨디셔너) / 자이로 / EKF  | 수신(1 s) 휠·컨디·IMU·EKF')
prev = dict(cnt)
while time.time() - t0 < 15.5:
    rclpy.spin_once(n, timeout_sec=0.02)
    if time.time() - t0 >= tick:
        def y(a, b):
            try: return yaw(tb.lookup_transform(a, b, rclpy.time.Time()).transform.rotation)
            except Exception: return float('nan')
        rc = {k: cnt[k] - prev[k] for k in cnt}; prev = dict(cnt)
        print('%2d  %+9.1f°  %+9.1f°  %+9.1f°  | %+.2f / %+.2f / %+.2f / %+.2f | %d·%d·%d·%d' % (
            tick, y('odom', 'base_link'), y('map', 'odom'), y('map', 'base_link'),
            last.get('/wheel_odom', float('nan')), last.get('/wheel_odom/conditioned', float('nan')), last.get('/imu/data', float('nan')), last.get('/odometry/filtered', float('nan')),
            rc['/wheel_odom'], rc['/wheel_odom/conditioned'], rc['/imu/data'], rc['/odometry/filtered']))
        tick += 1
