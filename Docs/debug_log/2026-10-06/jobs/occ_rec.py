#!/usr/bin/env python3
"""10-06 §10: 합성 가림 재생 기록 — 시험 EKF B(/odometry/filtered), 진실 대용(/truth_odom), /cmd_vel. 인자: OUT SEC"""
import sys, time, math, numpy as np, rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Twist
from rclpy.parameter import Parameter
def yaw(q): return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
OUT, SEC = sys.argv[1], float(sys.argv[2])
rclpy.init(); n = Node('occ_rec', parameter_overrides=[Parameter('use_sim_time', Parameter.Type.BOOL, True)])
D = {'B': [], 'T': [], 'C': []}; st = lambda h: h.stamp.sec + h.stamp.nanosec * 1e-9
for k, tp in (('B', '/odometry/filtered'), ('T', '/truth_odom')):
    n.create_subscription(Odometry, tp, lambda m, k=k: D[k].append((st(m.header), m.pose.pose.position.x, m.pose.pose.position.y, yaw(m.pose.pose.orientation))), qos_profile_sensor_data)
n.create_subscription(Twist, '/cmd_vel', lambda m: D['C'].append((n.get_clock().now().nanoseconds * 1e-9, m.angular.z)), 50)
t0 = time.time()
while time.time() - t0 < SEC: rclpy.spin_once(n, timeout_sec=0.05)
np.savez(OUT, **{k: np.array(v) for k, v in D.items()}); print('B %d · T %d · cmd %d' % tuple(len(D[k]) for k in 'BTC'))
