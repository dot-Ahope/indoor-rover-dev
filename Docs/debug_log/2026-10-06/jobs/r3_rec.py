#!/usr/bin/env python3
"""10-06 R3: 정식 ekf.launch(rf2o:=true shadow:=true) 재생 검증 기록기 — /odometry/filtered(B), /odometry/ekf_a(A). 인자: OUT SEC"""
import sys, time, math, numpy as np, rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from rclpy.parameter import Parameter
def yaw(q): return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
OUT, SEC = sys.argv[1], float(sys.argv[2])
rclpy.init(); n = Node('r3_rec', parameter_overrides=[Parameter('use_sim_time', Parameter.Type.BOOL, True)])
D = {'A': [], 'B': []}
st = lambda h: h.stamp.sec + h.stamp.nanosec * 1e-9
for k, tp in (('B', '/odometry/filtered'), ('A', '/odometry/ekf_a')):
    n.create_subscription(Odometry, tp, lambda m, k=k: D[k].append((st(m.header), m.pose.pose.position.x, m.pose.pose.position.y, yaw(m.pose.pose.orientation))), 50)
t0 = time.time()
while time.time() - t0 < SEC: rclpy.spin_once(n, timeout_sec=0.05)
np.savez(OUT, A=np.array(D['A']), B=np.array(D['B'])); print('A %d · B %d' % (len(D['A']), len(D['B'])))
