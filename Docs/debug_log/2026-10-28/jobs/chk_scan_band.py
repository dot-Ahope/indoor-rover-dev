#!/usr/bin/env python3
"""chk_scan_band — 라이다 한 판을 map 으로 옮겨 로버 둘레 ±1.2 m 에 점을 찍는다(10-28 §13, 로버 안 움직임).
  전역 코스트맵 치명 칸(outputs/costmap_robot_1519b.txt)이 지금 라이다가 보는 물체인지 가린다. * 라이다 점 · @ 로버"""
import math, time, rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan
from tf2_ros import Buffer, TransformListener
rclpy.init(); n = Node('chk_scan_band'); got = []
n.create_subscription(LaserScan, '/scan', lambda m: got.append(m), qos_profile_sensor_data)
buf = Buffer(); TransformListener(buf, n); t0 = time.time(); tf = tl = None
while time.time() - t0 < 15 and (len(got) < 3 or tf is None or tl is None):
    rclpy.spin_once(n, timeout_sec=0.2)
    if got:
        try: tf = buf.lookup_transform('map', 'base_link', rclpy.time.Time()); tl = buf.lookup_transform('map', got[-1].header.frame_id, rclpy.time.Time())
        except Exception: pass
yaw = lambda q: math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
rx, ry = tf.transform.translation.x, tf.transform.translation.y
lx, ly, la = tl.transform.translation.x, tl.transform.translation.y, yaw(tl.transform.rotation)
G = set()
for m in got[-3:]:
    for k, r in enumerate(m.ranges):
        if not (m.range_min < r < m.range_max): continue
        a = la + m.angle_min + k * m.angle_increment; x, y = lx + r * math.cos(a), ly + r * math.sin(a)
        G.add((round((x - rx) / 0.05), round((y - ry) / 0.05)))
print('로버 map (%.2f, %.2f) · 라이다 3 판 · 가장 가까운 점 %.2f m' % (rx, ry, min(min([r for r in m.ranges if m.range_min < r < m.range_max]) for m in got[-3:])))
for k in range(24, -25, -1):
    print('  %+.2f %s' % (ry + k * 0.05, ''.join('@' if (j, k) == (0, 0) else '*' if (j, k) in G else '.' for j in range(-24, 25))))
