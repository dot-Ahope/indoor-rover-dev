#!/usr/bin/env python3
"""제자리 회전으로 map 기준 heading 을 맞춘다 (2026-09-11).
   후진 복귀를 반복하면 heading 이 조금씩 틀어지는데, job125 는 '현재 heading 기준 전방 D m'
   로 목표를 잡으므로 코스가 통째로 달라진다(job224 에서 목표가 (1.56,-0.30) 이 되어
   계획이 상자 뒤로 붙었다). 시행 사이에 heading 을 같은 값으로 되돌려 조건을 고정한다.
   사용: python3 job225_face.py [목표heading_deg=0] [허용오차deg=1.5]"""
import sys
import time
import math
import rclpy
import tf2_ros
from rclpy.node import Node
from geometry_msgs.msg import Twist

TARGET = math.radians(float(sys.argv[1]) if len(sys.argv) > 1 else 0.0)
TOL = math.radians(float(sys.argv[2]) if len(sys.argv) > 2 else 1.5)
WMAX, WMIN = 0.30, 0.12

rclpy.init()
n = Node('face225')
buf = tf2_ros.Buffer()
tl = tf2_ros.TransformListener(buf, n)
pub = n.create_publisher(Twist, '/cmd_vel', 10)


def yaw():
    try:
        q = buf.lookup_transform('map', 'base_link', rclpy.time.Time()).transform.rotation
        return math.atan2(2*(q.w*q.z + q.x*q.y), 1 - 2*(q.y*q.y + q.z*q.z))
    except Exception:
        return None


t0 = time.time()
while time.time() - t0 < 10 and yaw() is None:
    rclpy.spin_once(n, timeout_sec=0.1)
y = yaw()
if y is None:
    print('TF 실패')
    raise SystemExit(1)
err0 = (TARGET - y + math.pi) % (2*math.pi) - math.pi
print('현재 hd %+.2f deg → 목표 %+.2f deg (회전 필요 %+.2f deg)'
      % (math.degrees(y), math.degrees(TARGET), math.degrees(err0)))
if abs(err0) <= TOL:
    print('이미 허용오차 안 — 회전 없음')
    raise SystemExit(0)

cmd = Twist()
t0 = time.time()
LIMIT = abs(err0) / WMIN + 25.0
while time.time() - t0 < LIMIT:
    rclpy.spin_once(n, timeout_sec=0.02)
    y = yaw()
    if y is None:
        continue
    err = (TARGET - y + math.pi) % (2*math.pi) - math.pi
    if abs(err) <= TOL:
        break
    # 목표에 가까워지면 감속 (오버슈트 방지)
    w = max(WMIN, min(WMAX, abs(err) * 1.2))
    cmd.angular.z = w if err > 0 else -w
    pub.publish(cmd)
z = Twist()
for _ in range(6):
    pub.publish(z)
    time.sleep(0.05)
time.sleep(0.4)
y = yaw()
print('완료: hd %+.2f deg (오차 %+.2f deg)'
      % (math.degrees(y), math.degrees((TARGET - y + math.pi) % (2*math.pi) - math.pi)))
