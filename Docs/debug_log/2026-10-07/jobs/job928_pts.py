#!/usr/bin/env python3
# 10-07 §8.4: 상자 ② 자리(map x 1.05~1.35, y −0.30~+0.10)에 지금 카메라 점(z 0.06~0.40)이 있나 — 5 s 동안 프레임별 점 수(읽기만)
import rclpy, numpy as np, time, math, tf2_ros
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import PointCloud2
from sensor_msgs_py import point_cloud2 as pc2
rclpy.init(); n = Node('chk928'); buf = tf2_ros.Buffer(); tf2_ros.TransformListener(buf, n); C = []
def cb(m):
    try: tr = buf.lookup_transform('map', m.header.frame_id, rclpy.time.Time()).transform
    except Exception: return
    q = tr.rotation; R = np.array([[1-2*(q.y*q.y+q.z*q.z), 2*(q.x*q.y-q.z*q.w), 2*(q.x*q.z+q.y*q.w)], [2*(q.x*q.y+q.z*q.w), 1-2*(q.x*q.x+q.z*q.z), 2*(q.y*q.z-q.x*q.w)], [2*(q.x*q.z-q.y*q.w), 2*(q.y*q.z+q.x*q.w), 1-2*(q.x*q.x+q.y*q.y)]])
    P = np.array([[p[0], p[1], p[2]] for p in pc2.read_points(m, field_names=('x', 'y', 'z'), skip_nans=True)])
    if not len(P): C.append((0, 0)); return
    W = P @ R.T + [tr.translation.x, tr.translation.y, tr.translation.z]
    box = (W[:, 0] > 1.05) & (W[:, 0] < 1.35) & (W[:, 1] > -0.30) & (W[:, 1] < 0.10)
    C.append((int((box & (W[:, 2] > 0.06) & (W[:, 2] < 0.40)).sum()), int((box & (W[:, 2] <= 0.06)).sum())))
n.create_subscription(PointCloud2, '/camera/depth/points_filtered', cb, qos_profile_sensor_data)
t = time.time()
while time.time() - t < 6: rclpy.spin_once(n, timeout_sec=0.05)
print('프레임 %d | 상자 ② 자리 점 수(높이 0.06~0.40): %s | 같은 자리 바닥 높이 점(≤0.06): %s' % (len(C), [c[0] for c in C][:20], [c[1] for c in C][:10]))
