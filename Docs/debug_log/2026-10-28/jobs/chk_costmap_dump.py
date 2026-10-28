#!/usr/bin/env python3
"""chk_costmap_dump — 전역 코스트맵 · 정적 /map 한 판과 로버 자세를 /tmp/gcm_dump.npz 로 (10-28 §16, 로버 안 움직임)"""
import time, numpy as np, rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, DurabilityPolicy, ReliabilityPolicy
from nav_msgs.msg import OccupancyGrid
from tf2_ros import Buffer, TransformListener
rclpy.init(); n = Node('chk_costmap_dump'); G = {}
q = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL, reliability=ReliabilityPolicy.RELIABLE)
for t in ('/global_costmap/costmap', '/map'): n.create_subscription(OccupancyGrid, t, lambda m, t=t: G.__setitem__(t, m), q)
buf = Buffer(); TransformListener(buf, n); t0 = time.time(); tf = None
while time.time() - t0 < 20 and (len(G) < 2 or tf is None):
    rclpy.spin_once(n, timeout_sec=0.2)
    try: tf = buf.lookup_transform('map', 'base_link', rclpy.time.Time())
    except Exception: pass
d = {}
for k, m in G.items():
    i = m.info; p = k.strip('/').replace('/', '_')
    d[p] = np.array(m.data, np.int16).reshape(i.height, i.width); d[p + '_o'] = np.array([i.origin.position.x, i.origin.position.y, i.resolution])
q_ = tf.transform.rotation; import math
d['robot'] = np.array([tf.transform.translation.x, tf.transform.translation.y, math.atan2(2 * (q_.w * q_.z), 1 - 2 * q_.z * q_.z)])
np.savez_compressed('/tmp/gcm_dump.npz', **d); print('저장', list(d), d['robot'])
