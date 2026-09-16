#!/usr/bin/env python3
"""상자 왼쪽 가장자리 셀 깜빡임의 출처 — 필터된 깊이 구름을 odom(코스트맵 격자, 0.05 m, 원점 정렬)으로 옮겨
   **STVL 이 보는 것과 같은 월드 복셀** 단위로 프레임마다 점 수를 센다 (2026-09-16 §1.8). 로버는 움직이지 않는다.

  출력: 영역 x [X0,X1] × y [Y0,Y1] (차체≈odom, map->odom 0) 의 각 2D 셀(5 cm)에 대해
        - 점이 1개 이상 있는 프레임 비율, 같은 셀의 **한 z-복셀에 ≥2 / ≥3 점**이 있는 프레임 비율, 프레임당 최대 복셀 점수
        → STVL voxel_min_points 를 2·3 으로 두면 어느 셀이 남고 어느 셀이 사라지는지 예측한다.
  인자: X0 X1 Y0 Y1 [DUR=40] [TOPIC]
"""
import sys, os, math, time
import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import PointCloud2
from sensor_msgs_py import point_cloud2 as pc2
import tf2_ros

X0, X1, Y0, Y1 = [float(a) for a in sys.argv[1:5]]
DUR = float(sys.argv[5]) if len(sys.argv) > 5 else 40.0
TOPIC = sys.argv[6] if len(sys.argv) > 6 else '/camera/depth/points_filtered'
RES = 0.05; ZMIN, ZMAX = 0.06, 0.40   # STVL min/max_obstacle_height 와 동일
rclpy.init(); n = Node('voxstat333'); buf = tf2_ros.Buffer(); tl = tf2_ros.TransformListener(buf, n)
F = []
n.create_subscription(PointCloud2, TOPIC, lambda m: F.append(m), qos_profile_sensor_data)
t0 = time.time()
while time.time() - t0 < DUR:
    rclpy.spin_once(n, timeout_sec=0.1)
print('프레임 %d (%.0f s) 토픽 %s' % (len(F), DUR, TOPIC))
if not F:
    sys.exit(1)
fr = F[0].header.frame_id
T = buf.lookup_transform('odom', fr, rclpy.time.Time(), timeout=rclpy.duration.Duration(seconds=3.0)).transform
q = T.rotation; x_, y_, z_, w_ = q.x, q.y, q.z, q.w
R = np.array([[1 - 2 * (y_ * y_ + z_ * z_), 2 * (x_ * y_ - z_ * w_), 2 * (x_ * z_ + y_ * w_)],
              [2 * (x_ * y_ + z_ * w_), 1 - 2 * (x_ * x_ + z_ * z_), 2 * (y_ * z_ - x_ * w_)],
              [2 * (x_ * z_ - y_ * w_), 2 * (y_ * z_ + x_ * w_), 1 - 2 * (x_ * x_ + y_ * y_)]])
t = np.array([T.translation.x, T.translation.y, T.translation.z])
print('TF %s -> odom: 이동 (%.3f, %.3f, %.3f)' % (fr, *t))
nx = int(round((X1 - X0) / RES)); ny = int(round((Y1 - Y0) / RES))
any1 = np.zeros((ny, nx)); ge2 = np.zeros((ny, nx)); ge3 = np.zeros((ny, nx)); mx = np.zeros((ny, nx)); tot = np.zeros((ny, nx))
zlo = np.full((ny, nx), 9.0); zhi = np.zeros((ny, nx))
EVY = float(os.environ['EVENT_Y']) if os.environ.get('EVENT_Y') else None
events = []
t_first = F[0].header.stamp.sec + F[0].header.stamp.nanosec * 1e-9
for m in F:
    arr = pc2.read_points(m, field_names=('x', 'y', 'z'), skip_nans=True)   # Humble: 구조화 ndarray
    if arr.size == 0:
        continue
    P = np.stack([arr['x'], arr['y'], arr['z']], axis=1).astype(np.float64)
    W = P @ R.T + t
    sel = (W[:, 0] >= X0) & (W[:, 0] < X1) & (W[:, 1] >= Y0) & (W[:, 1] < Y1) & (W[:, 2] >= ZMIN) & (W[:, 2] <= ZMAX)
    W = W[sel]
    if EVY is not None:   # 희귀 사건 기록: y ≥ EVY 인 점이 있는 프레임 — 점 수·좌표·같은 월드 복셀 내 최대 점 수
        ev = W[W[:, 1] >= EVY]
        if ev.shape[0] > 0:
            ek = (np.floor(ev[:, 0] / RES).astype(np.int64) * 100000 + np.floor(ev[:, 1] / RES).astype(np.int64)) * 1000 + np.floor(ev[:, 2] / RES).astype(np.int64)
            _, ec = np.unique(ek, return_counts=True)
            events.append((m.header.stamp.sec + m.header.stamp.nanosec * 1e-9 - t_first, ev.shape[0], int(ec.max()), ' '.join('(%.2f,%.2f,%.2f)' % tuple(r) for r in ev[:4])))
    if W.shape[0] == 0:
        continue
    ix = np.floor(W[:, 0] / RES).astype(np.int64); iy = np.floor(W[:, 1] / RES).astype(np.int64); iz = np.floor(W[:, 2] / RES).astype(np.int64)
    key = (ix * 100000 + iy) * 1000 + iz
    uk, inv, cnt = np.unique(key, return_inverse=True, return_counts=True)
    cx = (uk // 1000) // 100000; cy = (uk // 1000) % 100000
    for k in range(uk.size):
        j = int(cy[k] - round(Y0 / RES)); i = int(cx[k] - round(X0 / RES))
        if 0 <= j < ny and 0 <= i < nx:
            any1[j, i] += 1; tot[j, i] += cnt[k]
            if cnt[k] >= 2: ge2[j, i] += 1
            if cnt[k] >= 3: ge3[j, i] += 1
            mx[j, i] = max(mx[j, i], cnt[k])
    # 같은 2D 셀에 z-복셀이 둘이면 any1 이 두 번 더해질 수 있다 → 프레임 단위로 클램프
    any1 = np.minimum(any1, len(F)); ge2 = np.minimum(ge2, len(F)); ge3 = np.minimum(ge3, len(F))
    for k in range(uk.size):
        j = int(cy[k] - round(Y0 / RES)); i = int(cx[k] - round(X0 / RES))
        if 0 <= j < ny and 0 <= i < nx:
            zs = W[inv == k, 2]; zlo[j, i] = min(zlo[j, i], zs.min()); zhi[j, i] = max(zhi[j, i], zs.max())
nf = len(F)
hdr = '   y\\x   ' + ' '.join('%6.2f' % (X0 + (i + 0.5) * RES) for i in range(nx))
for label, A in (('점≥1 프레임%', any1), ('복셀≥2 프레임%', ge2), ('복셀≥3 프레임%', ge3), ('프레임당 최대 복셀점', mx)):
    print('--- %s ---' % label); print(hdr)
    for j in range(ny - 1, -1, -1):
        row = []
        for i in range(nx):
            v = A[j, i]
            row.append('%6.0f' % (100.0 * v / nf) if 'frame' in label or '프레임%' in label else '%6.0f' % v)
        print('%6.2f   ' % (Y0 + (j + 0.5) * RES) + ' '.join(row))
print('--- z 범위 (min~max, 점이 있던 셀만) ---'); print(hdr)
for j in range(ny - 1, -1, -1):
    print('%6.2f   ' % (Y0 + (j + 0.5) * RES) + ' '.join(('%.2f~%.2f' % (zlo[j, i], zhi[j, i]))[:11].rjust(6) if any1[j, i] > 0 else '     -' for i in range(nx)))
if EVY is not None:
    print('--- 사건: y ≥ %.2f 점이 있던 프레임 %d / %d ---' % (EVY, len(events), nf))
    for e in events[:60]:
        print('  t=%6.1f s  점 %d  같은복셀최대 %d  %s' % e)
rclpy.shutdown()
