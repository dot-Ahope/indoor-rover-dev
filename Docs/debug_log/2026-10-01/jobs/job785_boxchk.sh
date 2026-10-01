#!/bin/bash
# 10-01 §8.36: prep 뒤 정지 상태에서 전역·로컬 코스트맵의 상자 자리 비용 확인
python3 - <<'PY'
import rclpy, numpy as np, time
from rclpy.node import Node
from rclpy.qos import QoSProfile, DurabilityPolicy, ReliabilityPolicy
from nav_msgs.msg import OccupancyGrid
rclpy.init(); n = Node('box_chk'); G = {}
q = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL, reliability=ReliabilityPolicy.RELIABLE)
for tp in ('/global_costmap/costmap', '/local_costmap/costmap'):
    n.create_subscription(OccupancyGrid, tp, lambda m, tp=tp: G.__setitem__(tp, m), q if 'global' in tp else 5)
t0 = time.time()
while time.time() - t0 < 8 and len(G) < 2: rclpy.spin_once(n, timeout_sec=0.2)
for tp, m in G.items():
    g = np.array(m.data).reshape(m.info.height, m.info.width); r = m.info.resolution
    def c(x, y):
        i, j = int((y - m.info.origin.position.y) / r), int((x - m.info.origin.position.x) / r)
        return g[i, j] if 0 <= i < g.shape[0] and 0 <= j < g.shape[1] else None
    box = [c(x, y) for x in (1.15, 1.2, 1.25) for y in (0.0, -0.09, -0.17)]
    print('  %s 상자 자리(1.15~1.25, 0~−0.17) 비용: %s' % (tp, box))
PY
