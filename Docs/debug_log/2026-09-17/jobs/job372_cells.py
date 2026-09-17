#!/usr/bin/env python3
"""로컬·전역 코스트맵 상자 영역(x 0.5~1.8, |y|<0.4) LETHAL 셀 목록 + 3 회(10 s 간격) 반복 — 앞쪽 셀이 잡음인지 지속인지"""
import time, numpy as np, rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, DurabilityPolicy, ReliabilityPolicy
from nav_msgs.msg import OccupancyGrid
rclpy.init(); n = Node('cells372'); G = {}
q = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL, reliability=ReliabilityPolicy.RELIABLE)
n.create_subscription(OccupancyGrid, '/local_costmap/costmap', lambda m: G.__setitem__('l', m), q)
n.create_subscription(OccupancyGrid, '/global_costmap/costmap', lambda m: G.__setitem__('g', m), q)
for rep in range(2):
    G.clear(); t0 = time.time()
    while len(G) < 2 and time.time() - t0 < 12: rclpy.spin_once(n, timeout_sec=0.2)
    for k, name in (('l', '로컬'), ('g', '전역')):
        if k not in G: continue
        g = G[k]; d = np.array(g.data, dtype=np.int16).reshape(g.info.height, g.info.width); jj, ii = np.where(d >= 100)
        X = g.info.origin.position.x + (ii + 0.5) * g.info.resolution; Y = g.info.origin.position.y + (jj + 0.5) * g.info.resolution
        s = (X > 0.5) & (X < 1.8) & (np.abs(Y) < 0.4)
        cells = sorted(zip(np.round(X[s], 3), np.round(Y[s], 3), d[jj[s], ii[s]]))
        print('%s #%d %s: %s' % (name, rep, time.strftime('%T'), ' '.join('(%.3f,%+.3f,%d)' % c for c in cells)))
    time.sleep(8)
