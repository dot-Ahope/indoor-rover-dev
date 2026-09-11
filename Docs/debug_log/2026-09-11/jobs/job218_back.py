#!/usr/bin/env python3
"""접근 실험 후 같은 거리만큼 후진 복귀 — 다음 시행을 같은 조건에서 시작하기 위함.
   손으로 옮기면 스택 재초기화(약 70초)가 필요하고 SLAM 지도가 매번 새로 만들어져
   드리프트 조건이 달라진다. 자율 후진이면 지도를 유지한 채 같은 자리로 돌아온다.
   사용: python3 job218_back.py <거리m>"""
import sys
import time
import math
import rclpy
import tf2_ros
from rclpy.node import Node
from geometry_msgs.msg import Twist

D = float(sys.argv[1]) if len(sys.argv) > 1 else 0.0
if D <= 0.005:
    print('복귀 거리 0 — 할 일 없음')
    raise SystemExit(0)

rclpy.init()
n = Node('back218')
buf = tf2_ros.Buffer()
tl = tf2_ros.TransformListener(buf, n)
pub = n.create_publisher(Twist, '/cmd_vel', 10)


def pose():
    try:
        t = buf.lookup_transform('map', 'base_link', rclpy.time.Time()).transform
        return (t.translation.x, t.translation.y)
    except Exception:
        return None


t0 = time.time()
while time.time() - t0 < 10 and pose() is None:
    rclpy.spin_once(n, timeout_sec=0.1)
p0 = pose()
if p0 is None:
    print('TF 실패')
    raise SystemExit(1)

cmd = Twist()
cmd.linear.x = -0.04
t0 = time.time()
limit = D / 0.04 + 15.0
while time.time() - t0 < limit:
    rclpy.spin_once(n, timeout_sec=0.02)
    pub.publish(cmd)
    p = pose()
    if p and math.hypot(p[0] - p0[0], p[1] - p0[1]) >= D:
        break
z = Twist()
for _ in range(5):
    pub.publish(z)
    time.sleep(0.05)
p = pose()
moved = math.hypot(p[0] - p0[0], p[1] - p0[1]) if p else -1.0
print('복귀 완료: %.3f m (목표 %.3f)' % (moved, D))
