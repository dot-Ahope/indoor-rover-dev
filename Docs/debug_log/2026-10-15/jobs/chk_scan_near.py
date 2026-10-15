#!/usr/bin/env python3
"""chk_scan_near — 라이다 점 중 차체 직사각형(0.25/-0.25/±0.165)에 가장 가까운 10 개(몸체 좌표, 여유 cm). 로버 안 움직임."""
import time, numpy as np, rclpy, tf2_ros
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan
def qmat(q):
    x, y, z, w = q.x, q.y, q.z, q.w
    return np.array([[1-2*(y*y+z*z), 2*(x*y-z*w), 2*(x*z+y*w)], [2*(x*y+z*w), 1-2*(x*x+z*z), 2*(y*z-x*w)], [2*(x*z-y*w), 2*(y*z+x*w), 1-2*(x*x+y*y)]])
rclpy.init(); n = rclpy.create_node('chk_scan_near'); b = tf2_ros.Buffer(); tl = tf2_ros.TransformListener(b, n); S = [None]
n.create_subscription(LaserScan, '/scan', lambda m: S.__setitem__(0, m), qos_profile_sensor_data)
t0 = time.time()
while time.time() - t0 < 2.5: rclpy.spin_once(n, timeout_sec=0.05)
m = S[0]; t = b.lookup_transform('base_link', m.header.frame_id, rclpy.time.Time()).transform
T = np.array([t.translation.x, t.translation.y, t.translation.z]); R = qmat(t.rotation)
r = np.array(m.ranges); an = m.angle_min + np.arange(len(r)) * m.angle_increment; ok = np.isfinite(r) & (r > m.range_min) & (r < 1.5)
print('frame %s · T %s · yaw %.1f° · R22 %.2f' % (m.header.frame_id, np.round(T,3), np.degrees(np.arctan2(R[1,0],R[0,0])), R[2,2])); print('range_min %.3f · 유효 점 %d' % (m.range_min, ok.sum()))
rr = None
p = np.stack([r[ok]*np.cos(an[ok]), r[ok]*np.sin(an[ok]), np.zeros(ok.sum())], 1) @ R.T + T
k0 = p[:,0] > -0.20; p = p[k0]; rr = r[ok][k0]
d = np.hypot(np.maximum(np.maximum(-0.25-p[:,0], p[:,0]-0.25), 0), np.maximum(np.abs(p[:,1])-0.165, 0))
for k in np.argsort(d)[:10]: print('몸체 (%.3f, %.3f) · 원거리 %.3f m · 여유 %.1f cm' % (p[k,0], p[k,1], rr[k], 100*d[k]))
