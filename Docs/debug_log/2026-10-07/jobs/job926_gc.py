#!/usr/bin/env python3
# 10-07 §8.3: 전역 코스트맵 상자 근처 값과 발행 간격(읽기만) — 두 구독 방식(최초 래치 vs 이후 갱신) 비교
import rclpy, numpy as np, time
from rclpy.node import Node
from rclpy.qos import QoSProfile, DurabilityPolicy
from nav_msgs.msg import OccupancyGrid
rclpy.init(); n = Node('chk926'); L = []
n.create_subscription(OccupancyGrid, '/global_costmap/costmap', lambda m: L.append((time.time(), m)), QoSProfile(depth=5, durability=DurabilityPolicy.TRANSIENT_LOCAL))
t = time.time()
while time.time() - t < 12: rclpy.spin_once(n, timeout_sec=0.1)
print('12 s 동안 받은 전역 코스트맵 %d 개, stamp: %s' % (len(L), ' '.join('%.1f' % (m.header.stamp.sec % 1000 + m.header.stamp.nanosec * 1e-9) for _, m in L)))
if L:
    m = L[-1][1]; g = np.array(m.data).reshape(m.info.height, m.info.width); r = m.info.resolution; ox, oy = m.info.origin.position.x, m.info.origin.position.y
    ys = np.arange(-0.55, 0.45, 0.05); print('     y ' + ' '.join('%4.0f' % (100 * y) for y in ys))
    for x in np.arange(0.6, 1.8, 0.1): print('x %.1f ' % x + ' '.join('%4d' % g[int((y - oy) / r), int((x - ox) / r)] for y in ys))
