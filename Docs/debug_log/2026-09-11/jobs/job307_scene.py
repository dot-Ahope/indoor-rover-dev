#!/usr/bin/env python3
"""정지 상태 현장 지도: 깊이(z 0.06~0.40) 와 라이다를 base_link 5 cm 격자에 겹쳐 그린다 (2026-09-11). 로버는 움직이지 않는다."""
import sys, math, time
import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import PointCloud2, LaserScan
from sensor_msgs_py import point_cloud2 as pc2
import tf2_ros
rclpy.init(); n = Node('scene307'); buf = tf2_ros.Buffer(); tl = tf2_ros.TransformListener(buf, n)
F = []; S = []
n.create_subscription(PointCloud2, '/camera/camera/depth/color/points', lambda m: F.append(m), qos_profile_sensor_data)
n.create_subscription(LaserScan, '/scan', lambda m: S.append(m), qos_profile_sensor_data)
t0 = time.time()
while time.time() - t0 < 4.0:
    rclpy.spin_once(n, timeout_sec=0.05)
def tf_of(frame):
    tr = buf.lookup_transform('base_link', frame, rclpy.time.Time(), timeout=rclpy.duration.Duration(seconds=3.0)).transform
    q = tr.rotation
    R = np.array([[1-2*(q.y*q.y+q.z*q.z), 2*(q.x*q.y-q.z*q.w), 2*(q.x*q.z+q.y*q.w)],[2*(q.x*q.y+q.z*q.w), 1-2*(q.x*q.x+q.z*q.z), 2*(q.y*q.z-q.x*q.w)],[2*(q.x*q.z-q.y*q.w), 2*(q.y*q.z+q.x*q.w), 1-2*(q.x*q.x+q.y*q.y)]])
    return R, np.array([tr.translation.x, tr.translation.y, tr.translation.z])
step = 0.05; fw = np.arange(2.0, -0.35, -step); lat = np.arange(1.4, -0.85, -step)
D = np.zeros((len(fw), len(lat)), int); L = np.zeros_like(D); Z = np.zeros((len(fw), len(lat)))
R, T = tf_of(F[0].header.frame_id)
for m in F[-30:]:
    P = pc2.read_points_numpy(m, field_names=('x','y','z'), skip_nans=True) @ R.T + T
    P = P[(P[:,2] >= 0.06) & (P[:,2] < 0.40)]
    for x, y, z in P:
        a = int(round((2.0 - x) / step)); b = int(round((1.4 - y) / step))
        if 0 <= a < len(fw) and 0 <= b < len(lat):
            D[a, b] += 1; Z[a, b] = max(Z[a, b], z)
R2, T2 = tf_of(S[0].header.frame_id); yaw = math.atan2(R2[1,0], R2[0,0])
for s in S[-5:]:
    rr = np.array(s.ranges); ang = s.angle_min + np.arange(len(rr)) * s.angle_increment
    ok = np.isfinite(rr) & (rr > s.range_min) & (rr < s.range_max)
    x = T2[0] + rr[ok]*np.cos(ang[ok]+yaw); y = T2[1] + rr[ok]*np.sin(ang[ok]+yaw)
    for xi, yi in zip(x, y):
        a = int(round((2.0 - xi) / step)); b = int(round((1.4 - yi) / step))
        if 0 <= a < len(fw) and 0 <= b < len(lat):
            L[a, b] += 1
print('깊이 30프레임 누적(셀당 점 ≥ 15 만 표시: d=깊이만, L=라이다만, X=둘 다; 숫자=깊이 최대높이 dm). R=로버 중심, 차폭 0.33')
hdr = ''.join(('|' if abs(l - round(l*2)/2) < 1e-6 else ' ') for l in lat)
print('      횡: ' + hdr + '  (| = +1.0 +0.5 0 -0.5)')
for a, f in enumerate(fw):
    row = ''
    for b, l in enumerate(lat):
        d = D[a, b] >= 15; li = L[a, b] >= 1
        c = 'X' if d and li else ('d' if d else ('L' if li else ' '))
        if abs(f) < 0.03 and abs(l) < 0.03: c = 'R'
        row += c
    print('  %+5.2f %s' % (f, row))
print('깊이 최대높이(dm) 상위 셀:')
idx = np.dstack(np.unravel_index(np.argsort(-Z.ravel()), Z.shape))[0][:12]
for a, b in idx:
    if Z[a, b] > 0: print('   전방 %+.2f 횡 %+.2f  높이 %.2f m  점 %d' % (fw[a], lat[b], Z[a, b], D[a, b]))
