#!/usr/bin/env python3
"""09-29 §13 G3b 받침대 시험: 트랙이 공중에서 도는 상태(몸 정지)에서 stuck_monitor(그림자 모드)가 정체를 잡는지.
   순서: 정지 3 s → 직진 0.07 m/s 6 s → 정지 7 s(쿨다운 5 s 넘김) → 회전 0.3 rad/s 6 s → 정지 3 s. /cmd_vel 20 Hz.
   기록: /rover/stuck 판정 시각(구간 시작 기준), 휠 속도(트랙이 도는지), 자이로 yaw(몸이 안 도는지).
   판정: 직진·회전 구간 각각 시작 후 ≤ 3 s 에 판정 ≥ 1."""
import time, math
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from sensor_msgs.msg import Imu
from diagnostic_msgs.msg import DiagnosticArray

rclpy.init(); n = Node('stand_test')
pub = n.create_publisher(Twist, '/cmd_vel', 10)
ev, wv, gz = [], [], []
n.create_subscription(DiagnosticArray, '/rover/stuck', lambda m: [ev.append((time.time(), s.message)) for s in m.status], 10)
n.create_subscription(Odometry, '/wheel_odom', lambda m: wv.append((time.time(), m.twist.twist.linear.x, m.twist.twist.angular.z)), qos_profile_sensor_data)
n.create_subscription(Imu, '/imu/data', lambda m: gz.append((time.time(), -m.angular_velocity.y)), qos_profile_sensor_data)
plan = [('정지', 0.0, 0.0, 3.0), ('직진', 0.07, 0.0, 6.0), ('정지', 0.0, 0.0, 7.0), ('회전', 0.0, 0.3, 6.0), ('정지', 0.0, 0.0, 3.0)]
seg = []
for name, v, w, d in plan:
    t0 = time.time(); seg.append((name, t0, t0 + d))
    while time.time() - t0 < d:
        m = Twist(); m.linear.x = v; m.angular.z = w; pub.publish(m)
        te = time.time() + 0.05
        while time.time() < te: rclpy.spin_once(n, timeout_sec=0.01)
for _ in range(5): pub.publish(Twist()); time.sleep(0.05)
for name, a, b in seg:
    ww = [x for x in wv if a + 1 <= x[0] <= b]; gg = [x for x in gz if a + 1 <= x[0] <= b]
    wvm = sum(abs(x[1]) for x in ww) / len(ww) if ww else float('nan'); wwm = sum(abs(x[2]) for x in ww) / len(ww) if ww else float('nan')
    gm = sum(abs(x[1]) for x in gg) / len(gg) if gg else float('nan')
    hits = ['%.1f s: %s' % (t - a, msg) for t, msg in ev if a <= t <= b + 0.5]
    print('%s %.0f s | 휠 |v| %.3f m/s |ω| %.2f rad/s | 자이로 |ω| %.3f rad/s | 판정 %d 건 %s' % (name, b - a, wvm, wwm, gm, len(hits), '; '.join(hits)))
print('전체 판정 %d 건' % len(ev))
