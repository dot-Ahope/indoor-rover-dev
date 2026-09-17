#!/usr/bin/env python3
"""제자리 회전 스윕 여유 (2026-09-17 저속 실측 전): 로컬 코스트맵 LETHAL 셀과 base 중심 거리 최소값.
   풋프린트 반대각 0.30 m(0.25×0.165) — 회전 중 모서리가 그리는 원. 여유 = 최근접 셀 거리 − 0.30 − 셀 반폭 0.025."""
import time, math, numpy as np, rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, DurabilityPolicy, ReliabilityPolicy
from nav_msgs.msg import OccupancyGrid
import tf2_ros
rclpy.init(); n = Node('rotclear400'); buf = tf2_ros.Buffer(); tl = tf2_ros.TransformListener(buf, n); G = {}
n.create_subscription(OccupancyGrid, '/local_costmap/costmap', lambda m: G.__setitem__('g', m), QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL, reliability=ReliabilityPolicy.RELIABLE))
t0 = time.time()
while time.time() - t0 < 12 and ('g' not in G or not buf.can_transform('odom', 'base_link', rclpy.time.Time())):
    rclpy.spin_once(n, timeout_sec=0.2)
g = G['g']; t = buf.lookup_transform(g.header.frame_id, 'base_link', rclpy.time.Time()).transform
d = np.array(g.data, dtype=np.int16).reshape(g.info.height, g.info.width); jj, ii = np.where(d >= 100)
X = g.info.origin.position.x + (ii + .5) * g.info.resolution - t.translation.x; Y = g.info.origin.position.y + (jj + .5) * g.info.resolution - t.translation.y
r = np.hypot(X, Y); k = int(np.argmin(r))
q = t.rotation; yaw = math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
bx = X[k] * math.cos(yaw) + Y[k] * math.sin(yaw); by = -X[k] * math.sin(yaw) + Y[k] * math.cos(yaw)
print('최근접 LETHAL: 거리 %.3f m (차체 기준 x %+.2f, y %+.2f) | 회전 스윕 여유 %.3f m | 0.6 m 이내 셀 %d' % (r[k], bx, by, r[k] - 0.30 - 0.025, int((r < 0.6).sum())))
print('OK' if r[k] - 0.30 - 0.025 >= 0.05 else 'FAIL')
