import rosbag2_py, numpy as np
from rclpy.serialization import deserialize_message
from sensor_msgs.msg import Imu
from nav_msgs.msg import Odometry
r = rosbag2_py.SequentialReader(); r.open(rosbag2_py.StorageOptions(uri='/tmp/bag_f2b4', storage_id='sqlite3'), rosbag2_py.ConverterOptions('cdr', 'cdr'))
I, W = [], []; fid = None
while r.has_next():
    tp, d, ts = r.read_next()
    if tp == '/imu/data':
        m = deserialize_message(d, Imu); fid = m.header.frame_id; a = m.angular_velocity; I.append((ts * 1e-9, a.x, a.y, a.z))
    elif tp == '/wheel_odom':
        m = deserialize_message(d, Odometry); W.append((ts * 1e-9, m.twist.twist.angular.z))
I = np.array(I); W = np.array(W); wi = np.interp(I[:, 0], W[:, 0], W[:, 1]); m = abs(wi) > 0.2
print('imu frame', fid, '표본', m.sum())
for k, nm in ((1, 'x'), (2, 'y'), (3, 'z')): print('  ω_%s / 휠 ω 중앙 %.3f' % (nm, np.median(I[m, k] / wi[m])))
