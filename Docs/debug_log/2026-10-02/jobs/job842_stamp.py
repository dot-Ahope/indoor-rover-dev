import rosbag2_py, numpy as np
from rclpy.serialization import deserialize_message
from nav_msgs.msg import Odometry
from sensor_msgs.msg import LaserScan
r = rosbag2_py.SequentialReader(); r.open(rosbag2_py.StorageOptions(uri='/tmp/bag_f2b4', storage_id='sqlite3'), rosbag2_py.ConverterOptions('cdr', 'cdr'))
D = {'/wheel_odom': [], '/scan': []}; F = {}
while r.has_next():
    tp, d, ts = r.read_next()
    if tp in D and len(D[tp]) < 300:
        m = deserialize_message(d, Odometry if tp == '/wheel_odom' else LaserScan)
        D[tp].append(ts * 1e-9 - (m.header.stamp.sec + m.header.stamp.nanosec * 1e-9)); F[tp] = (m.header.frame_id, getattr(m, 'child_frame_id', ''))
for k, v in D.items(): print(k, F[k], '수신 − 스탬프 중앙 %.3f s · 범위 %.3f~%.3f' % (np.median(v), min(v), max(v)))
