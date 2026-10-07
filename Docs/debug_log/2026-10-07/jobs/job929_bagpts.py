#!/usr/bin/env python3
"""10-07 §8.4: 상자 ② 자리(map x 1.05~1.35, y −0.30~+0.10)의 카메라 점 수를 bag_box1 에서 2 s 마다 — 치우기 전후.
   로버가 단계 4 동안 같은 자리라 지금 TF(map←카메라 광학)로 변환(읽기만). 같은 시각 전역 코스트맵 상자 ② 칸 수도."""
import rclpy, numpy as np, time, rosbag2_py, tf2_ros
from rclpy.node import Node
from rclpy.serialization import deserialize_message
from sensor_msgs.msg import PointCloud2
from nav_msgs.msg import OccupancyGrid
from sensor_msgs_py import point_cloud2 as pc2
rclpy.init(); n = Node('chk929'); buf = tf2_ros.Buffer(); tf2_ros.TransformListener(buf, n); tr = None; t = time.time()
while tr is None and time.time() - t < 8:
    rclpy.spin_once(n, timeout_sec=0.1)
    try: tr = buf.lookup_transform('map', 'camera_depth_optical_frame', rclpy.time.Time()).transform
    except Exception: pass
q = tr.rotation; R = np.array([[1-2*(q.y*q.y+q.z*q.z), 2*(q.x*q.y-q.z*q.w), 2*(q.x*q.z+q.y*q.w)], [2*(q.x*q.y+q.z*q.w), 1-2*(q.x*q.x+q.z*q.z), 2*(q.y*q.z-q.x*q.w)], [2*(q.x*q.z-q.y*q.w), 2*(q.y*q.z+q.x*q.w), 1-2*(q.x*q.x+q.y*q.y)]]); T = np.array([tr.translation.x, tr.translation.y, tr.translation.z])
r = rosbag2_py.SequentialReader(); r.open(rosbag2_py.StorageOptions(uri='/tmp/bag_box1', storage_id='sqlite3'), rosbag2_py.ConverterOptions('cdr', 'cdr'))
r.set_filter(rosbag2_py.StorageFilter(topics=['/camera/depth/points_filtered', '/global_costmap/costmap']))
last = 0; gc = -1; rows = []
while r.has_next():
    tp, data, ts = r.read_next(); tt = ts * 1e-9
    if tp == '/global_costmap/costmap':
        m = deserialize_message(data, OccupancyGrid); g = np.array(m.data, np.int16).reshape(m.info.height, m.info.width); res = m.info.resolution; ox, oy = m.info.origin.position.x, m.info.origin.position.y
        gc = int((g[int((-0.1 - oy) / res):int((0.1 - oy) / res) + 1, int((1.1 - ox) / res):int((1.3 - ox) / res) + 1] >= 99).sum()); continue
    if tt - last < 2.0: continue
    last = tt; m = deserialize_message(data, PointCloud2); P = np.array([[p[0], p[1], p[2]] for p in pc2.read_points(m, field_names=('x', 'y', 'z'), skip_nans=True)])
    W = P @ R.T + T; b = (W[:, 0] > 1.05) & (W[:, 0] < 1.35) & (W[:, 1] > -0.30) & (W[:, 1] < 0.10)
    rows.append((tt, int((b & (W[:, 2] > 0.06) & (W[:, 2] < 0.40)).sum()), int((b & (W[:, 2] <= 0.06)).sum()), gc))
for tt, a, f, g in rows:
    if time.strftime('%H:%M:%S', time.localtime(tt)) >= '14:03:00': print('%s 상자 높이 점 %4d · 바닥 점 %4d · 전역 상자② 칸 %d' % (time.strftime('%H:%M:%S', time.localtime(tt)), a, f, g))
