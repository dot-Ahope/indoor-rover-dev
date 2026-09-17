#!/usr/bin/env python3
"""코스트맵 상자 위치 비교(감사 스크립트 우회): 오늘 로컬 코스트맵 vs 어제 mp5 bag 출발 시 로컬 코스트맵.
   상자 영역(x 0.7~1.8, |y|<0.35, 라이다 안 닿는 낮은 장애물) LETHAL 셀의 x 최소·y 범위. 인자: BAG"""
import sys, time, math, numpy as np, rclpy, rosbag2_py
from rclpy.node import Node
from rclpy.qos import QoSProfile, DurabilityPolicy, ReliabilityPolicy
from rclpy.serialization import deserialize_message
from nav_msgs.msg import OccupancyGrid
def box(G, ox_, oy_):
    d = np.array(G.data, dtype=np.int16).reshape(G.info.height, G.info.width); jj, ii = np.where(d >= 100)
    X = G.info.origin.position.x + (ii + 0.5) * G.info.resolution - ox_; Y = G.info.origin.position.y + (jj + 0.5) * G.info.resolution - oy_
    s = (X > 0.7) & (X < 1.8) & (np.abs(Y) < 0.35)
    return (X[s].min(), X[s].max(), Y[s].min(), Y[s].max(), int(s.sum())) if s.any() else None
r = rosbag2_py.SequentialReader(); r.open(rosbag2_py.StorageOptions(uri=sys.argv[1], storage_id='sqlite3'), rosbag2_py.ConverterOptions('', ''))
k = 0
while r.has_next():
    topic, data, ts = r.read_next()
    if topic == '/local_costmap/costmap':
        k += 1
        if k in (3, 6):
            b = box(deserialize_message(data, OccupancyGrid), 0.0, 0.0)
            print('어제 mp5 출발 로컬 코스트맵(#%d): 상자 셀 x %.3f~%.3f, y %+.3f~%+.3f (%d셀)' % ((k,) + b) if b else '어제: 상자 셀 없음')
        if k > 6: break
rclpy.init(); n = Node('costbox371'); G = {}
n.create_subscription(OccupancyGrid, '/local_costmap/costmap', lambda m: G.__setitem__('g', m), QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL, reliability=ReliabilityPolicy.RELIABLE))
t0 = time.time()
while 'g' not in G and time.time() - t0 < 10: rclpy.spin_once(n, timeout_sec=0.2)
b = box(G['g'], 0.0, 0.0)
print('오늘 로컬 코스트맵(로버 odom 0,0): 상자 셀 x %.3f~%.3f, y %+.3f~%+.3f (%d셀)' % b if b else '오늘: 상자 셀 없음')
