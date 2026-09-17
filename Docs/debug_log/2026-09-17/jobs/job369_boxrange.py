#!/usr/bin/env python3
"""상자 거리 교차검증 (2026-09-17): 깊이 클러스터 0.96 m vs 컬러 영상 추정 1.38 m 불일치. 로버는 움직이지 않는다.

  (1) 원시 깊이 영상(/camera/camera/depth/image_rect_raw)에서 낮은 장애물 화소의 거리 분포 (포인트클라우드·릴레이·TF 우회)
      - 깊이 intrinsics 로 각 화소를 광학좌표로 역투영 → 높이(카메라 z 0.143 기준)가 0.03~0.13 m 이고 전방 0.5~2.5 m 인 화소
  (2) 원시 포인트클라우드(/camera/camera/depth/color/points) 와 필터 출력의 같은 조건 점 x 히스토그램 (base_link)
  (3) 현재 /scan 한 장을 /tmp/scan_now.npy 로 저장 (어제 mp5 출발 스캔과 정합용)
  (4) 카메라 파라미터: emitter, depth 프로파일
"""
import sys, time, math
import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image, CameraInfo, PointCloud2, LaserScan
from sensor_msgs_py import point_cloud2 as pc2
import tf2_ros

rclpy.init(); n = Node('boxrange369'); buf = tf2_ros.Buffer(); tl = tf2_ros.TransformListener(buf, n)
S = {'depth': [], 'info': None, 'raw': [], 'filt': [], 'scan': None}
n.create_subscription(Image, '/camera/camera/depth/image_rect_raw', lambda m: S['depth'].append(m), qos_profile_sensor_data)
n.create_subscription(CameraInfo, '/camera/camera/depth/camera_info', lambda m: S.__setitem__('info', m), qos_profile_sensor_data)
n.create_subscription(PointCloud2, '/camera/camera/depth/color/points', lambda m: S['raw'].append(m), qos_profile_sensor_data)
n.create_subscription(PointCloud2, '/camera/depth/points_filtered', lambda m: S['filt'].append(m), qos_profile_sensor_data)
n.create_subscription(LaserScan, '/scan', lambda m: S.__setitem__('scan', m), qos_profile_sensor_data)
t0 = time.time()
while time.time() - t0 < 6.0:
    rclpy.spin_once(n, timeout_sec=0.1)
print('수신: depth %d, info %s, raw %d, filt %d, scan %s' % (len(S['depth']), S['info'] is not None, len(S['raw']), len(S['filt']), S['scan'] is not None))

# (1) 원시 깊이 영상
if S['depth'] and S['info']:
    K = S['info'].k; fx, fy, cx, cy = K[0], K[4], K[2], K[5]
    print('depth intrinsics: %dx%d fx %.1f fy %.1f cx %.1f cy %.1f encoding %s' % (S['info'].width, S['info'].height, fx, fy, cx, cy, S['depth'][-1].encoding))
    ds = []
    for m in S['depth'][-20:]:
        a = np.frombuffer(m.data, dtype=np.uint16).reshape(m.height, m.width).astype(np.float64) * 0.001
        ds.append(a)
    D = np.median(np.stack(ds), axis=0)
    H, W = D.shape
    v, u = np.mgrid[0:H, 0:W]
    Z = D; X = (u - cx) / fx * Z; Y = (v - cy) / fy * Z          # 광학좌표: X 오른쪽, Y 아래, Z 앞
    height = 0.143 - Y                                          # 카메라 높이 0.143 기준 지면 위 높이 (피치 0 가정)
    sel = (Z > 0.3) & (Z < 2.5) & (height > 0.03) & (height < 0.13) & (np.abs(X) < 0.35)
    if sel.any():
        zs = Z[sel]; xs = X[sel]
        print('(1) 원시 깊이: 낮은 화소 %d개 — 카메라 거리 5/25/50/75/95%% = %s m, 가로 X %.2f~%.2f' % (sel.sum(), ' / '.join('%.3f' % q for q in np.percentile(zs, [5, 25, 50, 75, 95])), xs.min(), xs.max()))
        hist, edges = np.histogram(zs, bins=np.arange(0.3, 2.55, 0.1))
        print('    거리 히스토그램(0.1 m): ' + ' '.join('%.1f:%d' % (edges[i], hist[i]) for i in range(len(hist)) if hist[i]))
        print('    → base x 로 환산(카메라 x 0.232 + 거리): 중앙값 %.3f' % (0.232 + np.median(zs)))
    # 바닥(높이 < 0.02) 행별 거리 — 카메라 피치 검증: 바닥 화소는 Z = 0.143*fy/(v-cy)
    rows = []
    for r in range(int(cy) + 8, H, 6):
        zrow = D[r, int(W * 0.35):int(W * 0.65)]; zrow = zrow[zrow > 0]
        if zrow.size > 5:
            rows.append('v%d:%.2f(기대%.2f)' % (r, np.median(zrow), 0.143 * fy / (r - cy)))
    print('    바닥 행 거리(측정/피치0 기대): ' + ' '.join(rows[:8]))

# (2) 포인트클라우드 x 히스토그램 (base_link)
for key in ('raw', 'filt'):
    if not S[key]:
        continue
    m = S[key][-1]
    T = buf.lookup_transform('base_link', m.header.frame_id, rclpy.time.Time(), timeout=rclpy.duration.Duration(seconds=2.0)).transform
    q = T.rotation; qx, qy, qz, qw = q.x, q.y, q.z, q.w
    R = np.array([[1 - 2 * (qy * qy + qz * qz), 2 * (qx * qy - qz * qw), 2 * (qx * qz + qy * qw)],
                  [2 * (qx * qy + qz * qw), 1 - 2 * (qx * qx + qz * qz), 2 * (qy * qz - qx * qw)],
                  [2 * (qx * qz - qy * qw), 2 * (qy * qz + qx * qw), 1 - 2 * (qx * qx + qy * qy)]])
    arr = pc2.read_points(m, field_names=('x', 'y', 'z'), skip_nans=True)
    P = np.stack([arr['x'], arr['y'], arr['z']], axis=1).astype(np.float64) @ R.T + np.array([T.translation.x, T.translation.y, T.translation.z])
    s = (P[:, 2] > 0.03) & (P[:, 2] < 0.13) & (np.abs(P[:, 1]) < 0.35) & (P[:, 0] > 0.4) & (P[:, 0] < 2.6)
    if s.any():
        hist, edges = np.histogram(P[s, 0], bins=np.arange(0.4, 2.65, 0.1))
        print('(2) %s 구름 낮은 점 %d개: base x 중앙값 %.3f, y %.2f~%.2f | x 히스토그램 %s' % (key, s.sum(), np.median(P[s, 0]), P[s, 1].min(), P[s, 1].max(), ' '.join('%.1f:%d' % (edges[i], hist[i]) for i in range(len(hist)) if hist[i])))
    else:
        print('(2) %s 구름: 낮은 점 없음' % key)

# (3) 스캔 저장
if S['scan'] is not None:
    sc = S['scan']
    np.save('/tmp/scan_now.npy', np.array([sc.angle_min, sc.angle_increment] + list(sc.ranges), dtype=np.float64))
    print('(3) /scan 저장: %d 빔, frame %s' % (len(sc.ranges), sc.header.frame_id))
rclpy.shutdown()
