#!/usr/bin/env python3
"""10-02 §14 R2: 기록기 — EKF A/B 출력, 라이브 TF(map→odom·odom→base), 스캔(2 Hz). 인자: OUT SEC"""
import sys, time, math, numpy as np, rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from tf2_msgs.msg import TFMessage
from sensor_msgs.msg import LaserScan
from rclpy.qos import qos_profile_sensor_data
from rclpy.parameter import Parameter
def yaw(q): return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
OUT, SEC = sys.argv[1], float(sys.argv[2])
rclpy.init(); n = Node('r2_rec', parameter_overrides=[Parameter('use_sim_time', Parameter.Type.BOOL, True)])
D = {'A': [], 'B': [], 'mo': [], 'ob': []}; SC = []; last = [0.0]
st = lambda h: h.stamp.sec + h.stamp.nanosec * 1e-9
for k in 'AB':
    n.create_subscription(Odometry, '/r2/ekf' + k, lambda m, k=k: D[k].append((st(m.header), m.pose.pose.position.x, m.pose.pose.position.y, yaw(m.pose.pose.orientation))), 50)
def cbt(m):
    for x in m.transforms:
        v = (st(x.header), x.transform.translation.x, x.transform.translation.y, yaw(x.transform.rotation))
        if (x.header.frame_id, x.child_frame_id) == ('map', 'odom'): D['mo'].append(v)
        elif (x.header.frame_id, x.child_frame_id) == ('odom', 'base_link'): D['ob'].append(v)
def cbs(m):
    t = st(m.header)
    if t - last[0] >= 0.5: last[0] = t; SC.append((t, np.array(m.ranges, dtype=np.float32), m.angle_min, m.angle_increment))
n.create_subscription(TFMessage, '/tf', cbt, 200); n.create_subscription(LaserScan, '/scan', cbs, qos_profile_sensor_data)
t0 = time.time()
while time.time() - t0 < SEC: rclpy.spin_once(n, timeout_sec=0.05)
np.savez(OUT, A=np.array(D['A']), B=np.array(D['B']), mo=np.array(D['mo']), ob=np.array(D['ob']),
         st=np.array([s[0] for s in SC]), sr=np.array([s[1] for s in SC]), sa=np.array([(s[2], s[3]) for s in SC]))
print('EKF A %d · B %d · map→odom %d · odom→base %d · 스캔 %d' % (len(D['A']), len(D['B']), len(D['mo']), len(D['ob']), len(SC)))
