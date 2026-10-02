#!/usr/bin/env python3
"""10-02 §6.3: G2 불합격(여유 0.067 m) 원인 — 로컬 코스트맵 99/100 칸 중 차체 외곽 0.25 m 안의 것을 로버 기준 좌표로 나열"""
import time, math, numpy as np, rclpy, tf2_ros
from rclpy.node import Node
from rclpy.qos import QoSProfile, DurabilityPolicy, ReliabilityPolicy
from nav_msgs.msg import OccupancyGrid
rclpy.init(); n = Node('near_cells'); buf = tf2_ros.Buffer(); tf2_ros.TransformListener(buf, n); G = {}
n.create_subscription(OccupancyGrid, '/local_costmap/costmap', lambda m: G.__setitem__('l', m), QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL, reliability=ReliabilityPolicy.RELIABLE))
t0 = time.time()
while time.time() - t0 < 8 and ('l' not in G or not buf.can_transform('odom', 'base_link', rclpy.time.Time())): rclpy.spin_once(n, timeout_sec=0.2)
m = G['l']; tr = buf.lookup_transform('odom', 'base_link', rclpy.time.Time()).transform
q = tr.rotation; th = math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z)); X, Y = tr.translation.x, tr.translation.y
g = np.array(m.data).reshape(m.info.height, m.info.width); r = m.info.resolution; ox, oy = m.info.origin.position.x, m.info.origin.position.y
ii, jj = np.where(g >= 100); wx = ox + (jj + .5) * r - X; wy = oy + (ii + .5) * r - Y; c, s = math.cos(th), math.sin(th)
bx, by = c * wx + s * wy, -s * wx + c * wy
dx = np.maximum(np.abs(bx) - 0.25, 0); dy = np.maximum(np.abs(by) - 0.165, 0); d = np.hypot(dx, dy)
k = np.argsort(d)[:15]
print('로컬 치명(100) 칸 %d, 차체 외곽 0.25 m 안 %d' % (len(d), (d < 0.25).sum()))
for i in k: print('  로버 기준 (%+.2f, %+.2f) 값 %d 외곽 거리 %.3f' % (bx[i], by[i], g[ii[i], jj[i]], d[i]))
