#!/usr/bin/env python3
"""로컬 코스트맵에서 상자 LETHAL 셀의 최대 y (차체좌표) — 창 게이트용 (2026-09-14 §2.16). 인자: BX BY"""
import sys, math, time, numpy as np, rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, DurabilityPolicy, ReliabilityPolicy
from nav_msgs.msg import OccupancyGrid
import tf2_ros
BX, BY = float(sys.argv[1]), float(sys.argv[2])
rclpy.init(); n = Node('boxcells315'); buf = tf2_ros.Buffer(); tl = tf2_ros.TransformListener(buf, n); G = {}
n.create_subscription(OccupancyGrid, '/local_costmap/costmap', lambda m: G.__setitem__('g', m), QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL, reliability=ReliabilityPolicy.RELIABLE))
t0 = time.time()
while time.time() - t0 < 15 and ('g' not in G or not buf.can_transform('odom', 'base_link', rclpy.time.Time())):
    rclpy.spin_once(n, timeout_sec=0.1)
if 'g' not in G: print('nan'); sys.exit(1)
g = G['g']; t = buf.lookup_transform(g.header.frame_id, 'base_link', rclpy.time.Time()).transform
q = t.rotation; yaw = math.atan2(2*(q.w*q.z+q.x*q.y), 1-2*(q.y*q.y+q.z*q.z))
d = np.array(g.data, dtype=np.int16).reshape(g.info.height, g.info.width); jj, ii = np.where(d >= 100)
X = g.info.origin.position.x + (ii + 0.5) * g.info.resolution; Y = g.info.origin.position.y + (jj + 0.5) * g.info.resolution
dx, dy = X - t.translation.x, Y - t.translation.y
bx = dx * math.cos(yaw) + dy * math.sin(yaw); by = -dx * math.sin(yaw) + dy * math.cos(yaw)
sel = (bx > BX - 0.15) & (bx < BX + 0.45) & (by > BY - 0.40) & (by < BY + 0.40)
print('%.3f' % by[sel].max() if sel.any() else 'nan')
