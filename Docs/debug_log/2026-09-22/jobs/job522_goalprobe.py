#!/usr/bin/env python3
"""목표 부근(base x 1.5~2.3, |y|<0.45) 에 무엇이 있나: 라이다 점·카메라 깊이 점·nvblox 슬라이스·전역/로컬 코스트맵을 한 번에 (2026-09-22 N6-1 G3 게이트 G1 실패 진단). 로버 정지 가정."""
import time, math, sys
import numpy as np, rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data, QoSProfile, DurabilityPolicy, ReliabilityPolicy
from sensor_msgs.msg import LaserScan, PointCloud2
from sensor_msgs_py import point_cloud2 as pc2
from nav_msgs.msg import OccupancyGrid
import tf2_ros
from nvblox_msgs.msg import DistanceMapSlice
X0, X1, Y0, Y1 = 1.5, 2.3, -0.45, 0.45
rclpy.init(); n = Node('goalprobe522'); buf = tf2_ros.Buffer(); tl = tf2_ros.TransformListener(buf, n); S = {}
tl_qos = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL, reliability=ReliabilityPolicy.RELIABLE)
n.create_subscription(LaserScan, '/scan', lambda m: S.__setitem__('scan', m), qos_profile_sensor_data)
n.create_subscription(PointCloud2, '/camera/camera/depth/color/points', lambda m: S.__setitem__('pc', m), qos_profile_sensor_data)
n.create_subscription(DistanceMapSlice, '/nvblox_node/static_map_slice', lambda m: S.__setitem__('sl', m), qos_profile_sensor_data)
n.create_subscription(OccupancyGrid, '/global_costmap/costmap', lambda m: S.__setitem__('g', m), tl_qos)
n.create_subscription(OccupancyGrid, '/local_costmap/costmap', lambda m: S.__setitem__('l', m), tl_qos)
t0 = time.time()
while time.time() - t0 < 12 and len(S) < 5: rclpy.spin_once(n, timeout_sec=0.1)
print('수신:', sorted(S.keys()))
t1 = time.time()   # TF 버퍼 채우기(첫 조회 전)
while time.time() - t1 < 6 and not (buf.can_transform('base_link', 'laser', rclpy.time.Time()) and buf.can_transform('map', 'base_link', rclpy.time.Time())): rclpy.spin_once(n, timeout_sec=0.1)
def T(frame):
    for _ in range(40):
        try:
            t = buf.lookup_transform(frame, 'base_link', rclpy.time.Time()).transform; q = t.rotation
            return t.translation.x, t.translation.y, math.atan2(2*(q.w*q.z+q.x*q.y), 1-2*(q.y*q.y+q.z*q.z))
        except Exception: rclpy.spin_once(n, timeout_sec=0.1)
    return None
def to_base(frame, X, Y):
    p = T(frame); c, s = math.cos(-p[2]), math.sin(-p[2]); X = X - p[0]; Y = Y - p[1]; return X*c - Y*s, X*s + Y*c
if 'scan' in S:
    m = S['scan']; a = m.angle_min + np.arange(len(m.ranges)) * m.angle_increment; r = np.asarray(m.ranges)
    ok = np.isfinite(r) & (r > 0.05); p = T('base_link') if False else None
    # 라이다 프레임→base_link
    tr = buf.lookup_transform('base_link', m.header.frame_id, rclpy.time.Time()).transform; q = tr.rotation; yaw = math.atan2(2*(q.w*q.z+q.x*q.y), 1-2*(q.y*q.y+q.z*q.z))
    xs = tr.translation.x + r[ok]*np.cos(a[ok]+yaw); ys = tr.translation.y + r[ok]*np.sin(a[ok]+yaw)
    sel = (xs > X0) & (xs < X1) & (ys > Y0) & (ys < Y1)
    print('라이다: 구역 안 점 %d개 %s' % (sel.sum(), [(round(float(x),2), round(float(y),2)) for x, y in zip(xs[sel][:10], ys[sel][:10])]))
if 'pc' in S:
    pts = np.array([(p[0], p[1], p[2]) for p in pc2.read_points(S['pc'], field_names=('x','y','z'), skip_nans=True)], dtype=np.float32)
    tr = buf.lookup_transform('base_link', S['pc'].header.frame_id, rclpy.time.Time()).transform; q = tr.rotation
    import numpy.linalg as la
    w,x,y,z = q.w,q.x,q.y,q.z; Rm = np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])
    P = pts @ Rm.T + np.array([tr.translation.x, tr.translation.y, tr.translation.z])
    sel = (P[:,0] > X0) & (P[:,0] < X1) & (P[:,1] > Y0) & (P[:,1] < Y1) & (P[:,2] > 0.03) & (P[:,2] < 0.6)
    if sel.sum(): print('카메라 점(z 0.03~0.6): %d개, x %.2f~%.2f y %+.2f~%+.2f z %.2f~%.2f' % (sel.sum(), P[sel,0].min(), P[sel,0].max(), P[sel,1].min(), P[sel,1].max(), P[sel,2].min(), P[sel,2].max()))
    else: print('카메라 점(z 0.03~0.6): 0개 (전체 %d)' % len(P))
for key, name in (('sl', 'nvblox 슬라이스'), ('g', '전역 코스트맵'), ('l', '로컬 코스트맵')):
    if key not in S: continue
    m = S[key]
    if key == 'sl':
        d = np.asarray(m.data, dtype=np.float32).reshape(m.height, m.width); jj, ii = np.indices(d.shape); res = m.resolution; ox, oy = m.origin.x, m.origin.y; fr = m.header.frame_id
    else:
        d = np.array(m.data, dtype=np.int16).reshape(m.info.height, m.info.width); jj, ii = np.indices(d.shape); res = m.info.resolution; ox, oy = m.info.origin.position.x, m.info.origin.position.y; fr = m.header.frame_id
    X = ox + (ii + 0.5) * res; Y = oy + (jj + 0.5) * res; bx, by = to_base(fr, X, Y)
    sel = (bx > X0) & (bx < X1) & (by > Y0) & (by < Y1)
    v = d[sel]
    if key == 'sl':
        unk = v == m.unknown_value; print('%s(%s): 구역 셀 %d, 미지 %d, ≤0(장애물) %d, 최소 거리 %s' % (name, fr, sel.sum(), unk.sum(), ((~unk) & (v <= 0)).sum(), ('%.2f' % v[~unk].min()) if (~unk).any() else '-'))
        ob = sel & (d <= 0) & (d != m.unknown_value); print('   ≤0 셀 위치(base):', [(round(float(a),2), round(float(b),2)) for a, b in zip(bx[ob][:12], by[ob][:12])])
    else:
        print('%s(%s): 구역 셀 %d, LETHAL(100) %d, 99 %d, 미지(-1) %d' % (name, fr, sel.sum(), (v == 100).sum(), (v == 99).sum(), (v < 0).sum()))
        le = sel & (d == 100); print('   LETHAL 위치(base):', [(round(float(a),2), round(float(b),2)) for a, b in zip(bx[le][:12], by[le][:12])])
rclpy.shutdown()
