#!/usr/bin/env python3
"""chk_costmap_robot — 전역 코스트맵 한 판에서 로버 자리 둘레 ±1.2 m 를 문자 격자로(10-28 §13, 로버 안 움직임).
  계획기(NavFn)가 모든 목표에 '경로 없음' 일 때 시작 칸이 치명인지 본다. # 100(치명) · + 99 · : 1~98 · . 0 · ? 미지 · @ 로버"""
import math, time, rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, DurabilityPolicy, ReliabilityPolicy
from nav_msgs.msg import OccupancyGrid
from tf2_ros import Buffer, TransformListener
rclpy.init(); n = Node('chk_costmap_robot'); got = []
n.create_subscription(OccupancyGrid, '/global_costmap/costmap', lambda m: got.append(m), QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL, reliability=ReliabilityPolicy.RELIABLE))
buf = Buffer(); TransformListener(buf, n); t0 = time.time(); tf = None
while time.time() - t0 < 15 and (not got or tf is None):
    rclpy.spin_once(n, timeout_sec=0.2)
    try: tf = buf.lookup_transform('map', 'base_link', rclpy.time.Time())
    except Exception: pass
m = got[-1]; i = m.info; rx, ry = tf.transform.translation.x, tf.transform.translation.y
print('로버 map (%.2f, %.2f) · 판 %dx%d res %.2f' % (rx, ry, i.width, i.height, i.resolution))
v = lambda x, y: m.data[int((y - i.origin.position.y) / i.resolution) * i.width + int((x - i.origin.position.x) / i.resolution)]
print('로버 칸 값', v(rx, ry))
for k in range(24, -25, -1):
    y = ry + k * 0.05; s = ''
    for j in range(-24, 25):
        x = rx + j * 0.05; c = v(x, y)
        s += '@' if (j == 0 and k == 0) else ('?' if c < 0 else '#' if c >= 100 else '+' if c >= 99 else ':' if c > 0 else '.')
    print('  %+.2f %s' % (y, s))
