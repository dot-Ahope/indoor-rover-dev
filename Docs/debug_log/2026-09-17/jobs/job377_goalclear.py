#!/usr/bin/env python3
"""목표 여유 게이트 (2026-09-17, mp6 교훈): 목표 자리에 로버 풋프린트를 놓았을 때 전역 코스트맵 LETHAL 셀까지 최소거리.
   목표는 시작 프레임 (D, LAT) → map (로버가 map 원점·yaw≈0 일 때). 풋프린트 반길이 0.26·반폭 0.175 직사각형 둘레 기준.
   출력 마지막 줄: 여유(m). 인자: D LAT [YAW_deg=0]"""
import sys, time, math, numpy as np, rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, DurabilityPolicy, ReliabilityPolicy
from nav_msgs.msg import OccupancyGrid
import tf2_ros
D, LAT = float(sys.argv[1]), float(sys.argv[2]); GYAW = math.radians(float(sys.argv[3])) if len(sys.argv) > 3 else 0.0
rclpy.init(); n = Node('goalclear377'); buf = tf2_ros.Buffer(); tl = tf2_ros.TransformListener(buf, n); G = {}
n.create_subscription(OccupancyGrid, '/global_costmap/costmap', lambda m: G.__setitem__('g', m), QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL, reliability=ReliabilityPolicy.RELIABLE))
t0 = time.time()
while time.time() - t0 < 12 and ('g' not in G or not buf.can_transform('map', 'base_link', rclpy.time.Time())):
    rclpy.spin_once(n, timeout_sec=0.2)
if 'g' not in G: print('nan'); sys.exit(1)
t = buf.lookup_transform('map', 'base_link', rclpy.time.Time()).transform
q = t.rotation; yaw = math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
gx = t.translation.x + D * math.cos(yaw) - LAT * math.sin(yaw); gy = t.translation.y + D * math.sin(yaw) + LAT * math.cos(yaw); gth = yaw + GYAW
g = G['g']; res = g.info.resolution; d = np.array(g.data, dtype=np.int16).reshape(g.info.height, g.info.width)
jj, ii = np.where(d >= 100); X = g.info.origin.position.x + (ii + .5) * res; Y = g.info.origin.position.y + (jj + .5) * res
# 목표 자세의 풋프린트 좌표로 옮겨 직사각형까지의 거리
dx, dy = X - gx, Y - gy; lx = dx * math.cos(gth) + dy * math.sin(gth); ly = -dx * math.sin(gth) + dy * math.cos(gth)
ex = np.maximum(np.abs(lx) - 0.26, 0); ey = np.maximum(np.abs(ly) - 0.175, 0); dist = np.hypot(ex, ey)
k = int(np.argmin(dist)) if dist.size else -1
print('목표 map (%.2f, %.2f) yaw %.0f° | 풋프린트↔LETHAL 최소 %.3f m (셀 map %.2f, %.2f) | 목표 셀 비용 %d' % (gx, gy, math.degrees(gth), dist[k] if k >= 0 else 9, X[k] if k >= 0 else 0, Y[k] if k >= 0 else 0, d[int((gy - g.info.origin.position.y) / res), int((gx - g.info.origin.position.x) / res)]))
print('%.3f' % (dist[k] if k >= 0 else 9.0))
