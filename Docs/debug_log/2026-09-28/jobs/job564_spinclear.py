#!/usr/bin/env python3
"""회전 시험 전 주변 여유 확인: 라이다 스캔을 차체 좌표로 바꿔 8 방위별 최근접 거리(차체 중심 기준)와 회전 반경(0.30 m) 밖 여유."""
import math, rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan
import tf2_ros
rclpy.init(); n = Node('spinclear'); buf = tf2_ros.Buffer(); tl = tf2_ros.TransformListener(buf, n); sc = []
n.create_subscription(LaserScan, '/scan', lambda m: sc.append(m), qos_profile_sensor_data)
import time; t0 = time.time()
while time.time() - t0 < 10 and (len(sc) < 5 or not buf.can_transform('base_link', 'lidar_link', rclpy.time.Time())): rclpy.spin_once(n, timeout_sec=0.1)
m = sc[-1]
try:
    t = buf.lookup_transform('base_link', m.header.frame_id, rclpy.time.Time()).transform
    q = t.rotation; yaw = math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z)); tx, ty = t.translation.x, t.translation.y
    flip = (abs(q.x) > 0.7 or abs(q.y) > 0.7)
except Exception as e:
    print('TF 실패', e); yaw, tx, ty, flip = math.pi, 0.0, 0.0, False
sec = {}
for i, r in enumerate(m.ranges):
    if not math.isfinite(r) or r < 0.15: continue
    a = m.angle_min + i * m.angle_increment
    x = tx + r * math.cos(a + yaw); y = ty + r * math.sin(a + yaw)
    d = math.hypot(x, y); b = int(((math.degrees(math.atan2(y, x)) + 382.5) % 360) // 45)
    if b not in sec or d < sec[b][0]: sec[b] = (d, x, y)
names = ['앞', '앞왼', '왼', '뒤왼', '뒤', '뒤오른', '오른', '앞오른']
for b in range(8):
    if b in sec: print('  %-4s 최근접 %.2f m (차체좌표 %+.2f, %+.2f) → 회전 반경 0.30 밖 여유 %.2f m' % (names[b], sec[b][0], sec[b][1], sec[b][2], sec[b][0] - 0.30))
print('  전체 최소 %.2f m' % min(v[0] for v in sec.values()))
rclpy.shutdown()
