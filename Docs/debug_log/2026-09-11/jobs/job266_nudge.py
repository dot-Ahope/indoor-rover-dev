#!/usr/bin/env python3
"""직선 미세 이동 — 상자 상대 게이트의 dx 를 맞추기 위해. 양수 전진 / 음수 후진. v=0.04.
   사용: python3 job266_nudge.py <거리m>"""
import sys, time, math, rclpy, tf2_ros
from rclpy.node import Node
from geometry_msgs.msg import Twist
D = float(sys.argv[1]) if len(sys.argv) > 1 else 0.0
if abs(D) < 0.01:
    print('이동 없음'); raise SystemExit(0)
rclpy.init(); n = Node('nudge266')
buf = tf2_ros.Buffer(); tl = tf2_ros.TransformListener(buf, n)
pub = n.create_publisher(Twist, '/cmd_vel', 10)
def pose():
    try:
        t = buf.lookup_transform('odom', 'base_link', rclpy.time.Time()).transform
        return (t.translation.x, t.translation.y)
    except Exception:
        return None
t0 = time.time()
while time.time() - t0 < 10 and pose() is None: rclpy.spin_once(n, timeout_sec=0.1)
p0 = pose()
if p0 is None: print('TF 실패'); raise SystemExit(1)
cmd = Twist(); cmd.linear.x = 0.04 if D > 0 else -0.04
t0 = time.time()
while time.time() - t0 < abs(D)/0.04 + 10:
    rclpy.spin_once(n, timeout_sec=0.02); pub.publish(cmd)
    p = pose()
    if p and math.hypot(p[0]-p0[0], p[1]-p0[1]) >= abs(D): break
z = Twist()
for _ in range(5): pub.publish(z); time.sleep(0.05)
p = pose()
print('이동 %.3f m (목표 %+.3f)' % (math.hypot(p[0]-p0[0], p[1]-p0[1]) if p else -1, D))
