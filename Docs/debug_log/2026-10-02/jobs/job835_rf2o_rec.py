#!/usr/bin/env python3
"""10-02 §13 R1: rf2o 재생 시험 기록기 — /odom_rf2o 와 /tf(map→odom, odom→base) 를 받아 npz 로. 인자: OUT SEC"""
import sys, time, math, numpy as np, rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from tf2_msgs.msg import TFMessage
from rclpy.parameter import Parameter
def yaw(q): return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
OUT, SEC = sys.argv[1], float(sys.argv[2])
rclpy.init(); n = Node('rf2o_rec', parameter_overrides=[Parameter('use_sim_time', Parameter.Type.BOOL, True)])
RF, MO, OB = [], [], []
def cb(m):
    t = m.header.stamp.sec + m.header.stamp.nanosec * 1e-9
    RF.append((t, m.pose.pose.position.x, m.pose.pose.position.y, yaw(m.pose.pose.orientation), m.twist.twist.linear.x, m.twist.twist.linear.y, m.twist.twist.angular.z))
def cbt(m):
    for x in m.transforms:
        t = x.header.stamp.sec + x.header.stamp.nanosec * 1e-9; v = (t, x.transform.translation.x, x.transform.translation.y, yaw(x.transform.rotation))
        if (x.header.frame_id, x.child_frame_id) == ('map', 'odom'): MO.append(v)
        elif (x.header.frame_id, x.child_frame_id) == ('odom', 'base_link'): OB.append(v)
n.create_subscription(Odometry, '/odom_rf2o', cb, 50); n.create_subscription(TFMessage, '/tf', cbt, 200)
t0 = time.time()
while time.time() - t0 < SEC: rclpy.spin_once(n, timeout_sec=0.05)
np.savez(OUT, rf=np.array(RF), mo=np.array(MO), ob=np.array(OB)); print('rf2o %d · map→odom %d · odom→base %d' % (len(RF), len(MO), len(OB)))
