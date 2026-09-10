#!/usr/bin/env python3
"""정지 상태 yaw 드리프트의 원천 — 축을 바로잡아 다시 잰다 (2026-09-10).
  ekf.yaml: imu0_config 인덱스 10(vpitch 자리) = camera_imu_optical_frame 의 -y = 로봇 yaw.
  즉 EKF 가 보는 것은 angular_velocity.y 이지 .z 가 아니다(앞선 측정의 실수).
  로버는 움직이지 않는다."""
import time, math, sys
import numpy as np
import rclpy, tf2_ros
from rclpy.node import Node
from sensor_msgs.msg import Imu
from nav_msgs.msg import Odometry
from rclpy.qos import qos_profile_sensor_data

DUR = float(sys.argv[1]) if len(sys.argv) > 1 else 30.0
rclpy.init(); n = Node('axis213')
buf = tf2_ros.Buffer(); tl = tf2_ros.TransformListener(buf, n)
A = {'raw': [], 'cond': [], 'wheel': []}
n.create_subscription(Imu, '/camera/camera/imu',
                      lambda m: A['raw'].append((m.angular_velocity.x, m.angular_velocity.y, m.angular_velocity.z)),
                      qos_profile_sensor_data)
n.create_subscription(Imu, '/imu/data',
                      lambda m: A['cond'].append((m.angular_velocity.x, m.angular_velocity.y, m.angular_velocity.z)),
                      qos_profile_sensor_data)
n.create_subscription(Odometry, '/wheel_odom',
                      lambda m: A['wheel'].append(m.twist.twist.angular.z), qos_profile_sensor_data)


def yaw(a, b):
    try:
        q = buf.lookup_transform(a, b, rclpy.time.Time()).transform.rotation
        return math.atan2(2*(q.w*q.z + q.x*q.y), 1 - 2*(q.y*q.y + q.z*q.z))
    except Exception:
        return None


t0 = time.time()
while time.time() - t0 < 10 and yaw('odom', 'base_link') is None:
    rclpy.spin_once(n, timeout_sec=0.1)
y0 = yaw('odom', 'base_link')
t0 = time.time()
while time.time() - t0 < DUR:
    rclpy.spin_once(n, timeout_sec=0.05)
y1 = yaw('odom', 'base_link')
el = time.time() - t0

raw = np.array(A['raw']); cond = np.array(A['cond']); wh = np.array(A['wheel'])
print('=== %.0f초 정지 ===' % el)
print('  샘플: /camera/camera/imu %d,  /imu/data %d,  /wheel_odom %d' % (len(raw), len(cond), len(wh)))
print()
for name, arr in (('원본 /camera/camera/imu', raw), ('보정 /imu/data', cond)):
    if len(arr) == 0:
        print('  %s: 없음' % name); continue
    m = arr.mean(axis=0); s = arr.std(axis=0)
    print('  %s' % name)
    print('    광학 wx %+.6f ±%.6f   wy %+.6f ±%.6f   wz %+.6f ±%.6f rad/s'
          % (m[0], s[0], m[1], s[1], m[2], s[2]))
    print('    → EKF 가 쓰는 로봇 yaw rate = -wy = %+.6f rad/s = %+.4f °/s = %+.2f °/분'
          % (-m[1], math.degrees(-m[1]), math.degrees(-m[1])*60))
if len(wh):
    print('  휠 vyaw 평균 %+.6f rad/s (정지이므로 0)' % wh.mean())
print()
d = (y1 - y0 + math.pi) % (2*math.pi) - math.pi
print('  EKF odom->base yaw 실측 변화: %+.5f rad / %.0f초 = %+.6f rad/s = %+.4f °/s = %+.2f °/분'
      % (d, el, d/el, math.degrees(d/el), math.degrees(d/el)*60))
if len(cond):
    pred = -cond.mean(axis=0)[1]
    print('  자이로 잔차로 예측한 값     : %+.6f rad/s = %+.2f °/분' % (pred, math.degrees(pred)*60))
    if abs(pred) > 1e-6:
        print('  설명 비율                   : %.0f%%' % (100.0*(d/el)/pred))
