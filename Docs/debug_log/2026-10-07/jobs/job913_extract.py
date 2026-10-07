#!/usr/bin/env python3
"""10-07 §3: f2c 주행 bag 전체 추출(③-b 번짐·③-c 게이트·보정량) — map→odom, odom→base(EKF B), 그림자 A, EKF B 속도, rf2o 원·게이트 출력(+공분산), cmd_vel, /plan 시각.
   인자: BAG OUT"""
import sys, math, numpy as np, rosbag2_py
from rclpy.serialization import deserialize_message
from rosidl_runtime_py.utilities import get_message
BAG, OUT = sys.argv[1], sys.argv[2]
r = rosbag2_py.SequentialReader(); r.open(rosbag2_py.StorageOptions(uri=BAG, storage_id='sqlite3'), rosbag2_py.ConverterOptions('cdr', 'cdr'))
types = {t.name: t.type for t in r.get_all_topics_and_types()}
def yaw(q): return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
D = {k: [] for k in ('mo', 'ob', 'A', 'Bv', 'raw', 'gated', 'cmd', 'plan')}
while r.has_next():
    tp, data, ts = r.read_next(); t = ts * 1e-9
    if tp not in ('/tf', '/odometry/ekf_a', '/odometry/filtered', '/odom_rf2o', '/odom_rf2o/gated', '/cmd_vel', '/plan'): continue
    m = deserialize_message(data, get_message(types[tp]))
    if tp == '/tf':
        for x in m.transforms:
            k = (x.header.frame_id, x.child_frame_id); v = (t, x.transform.translation.x, x.transform.translation.y, yaw(x.transform.rotation))
            if k == ('map', 'odom'): D['mo'].append(v)
            elif k == ('odom', 'base_link'): D['ob'].append(v)
    elif tp == '/odometry/ekf_a': p = m.pose.pose; D['A'].append((t, p.position.x, p.position.y, yaw(p.orientation)))
    elif tp == '/odometry/filtered': D['Bv'].append((t, m.twist.twist.linear.x, m.twist.twist.linear.y, m.twist.twist.angular.z))
    elif tp == '/odom_rf2o': D['raw'].append((t, m.twist.twist.linear.x, m.twist.twist.linear.y, m.twist.twist.angular.z))
    elif tp == '/odom_rf2o/gated': D['gated'].append((t, m.twist.twist.linear.x, m.twist.twist.linear.y, m.twist.covariance[0], m.twist.covariance[7]))
    elif tp == '/cmd_vel': D['cmd'].append((t, m.linear.x, m.angular.z))
    elif tp == '/plan': D['plan'].append((t, len(m.poses)))
np.savez_compressed(OUT, **{k: np.array(v) for k, v in D.items()}); print(OUT, {k: len(v) for k, v in D.items()})
