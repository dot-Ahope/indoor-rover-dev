#!/usr/bin/env python3
"""정지 상태 30 s: 로버 정면 바닥(전방 0.45~1.0, |횡| < 0.3, 물체 없음)에 z ≥ 0.06 깊이점이 생기는가 (2026-09-14).
  inf1 입구 정체의 '상자 앞 깊이 전용 7셀' 과 재기동 직후 감사의 '근거 없는 셀 (+0.62, +0.03)' 의 출처 후보 = 근거리 스테레오 잡음.
  프레임별 점 수, 위치(전방/횡/z), 카메라 거리 분포를 센다. 로버는 움직이지 않는다."""
import sys, time, math, numpy as np, rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import PointCloud2
from sensor_msgs_py import point_cloud2 as pc2
import tf2_ros
DUR = float(sys.argv[1]) if len(sys.argv) > 1 else 30.0
rclpy.init(); n = Node('floor311'); buf = tf2_ros.Buffer(); tl = tf2_ros.TransformListener(buf, n)
F = []
n.create_subscription(PointCloud2, '/camera/camera/depth/color/points', lambda m: F.append(m), qos_profile_sensor_data)
t0 = time.time()
while time.time() - t0 < DUR:
    rclpy.spin_once(n, timeout_sec=0.05)
tr = buf.lookup_transform('base_link', F[0].header.frame_id, rclpy.time.Time(), timeout=rclpy.duration.Duration(seconds=3.0)).transform
q = tr.rotation
R = np.array([[1-2*(q.y*q.y+q.z*q.z), 2*(q.x*q.y-q.z*q.w), 2*(q.x*q.z+q.y*q.w)],[2*(q.x*q.y+q.z*q.w), 1-2*(q.x*q.x+q.z*q.z), 2*(q.y*q.z-q.x*q.w)],[2*(q.x*q.z-q.y*q.w), 2*(q.y*q.z+q.x*q.w), 1-2*(q.x*q.x+q.y*q.y)]])
T = np.array([tr.translation.x, tr.translation.y, tr.translation.z])
hits = []; per = []
for k, m in enumerate(F):
    P = pc2.read_points_numpy(m, field_names=('x', 'y', 'z'), skip_nans=True) @ R.T + T
    x, y, z = P[:, 0], P[:, 1], P[:, 2]
    sel = (x > 0.45) & (x < 1.0) & (np.abs(y) < 0.3) & (z >= 0.06) & (z < 0.40)
    per.append(int(sel.sum()))
    for p in P[sel]:
        hits.append((k, p[0], p[1], p[2], math.hypot(p[0] - T[0], p[1] - T[1])))
nf = len(F)
print('프레임 %d (%.0f s). 정면 바닥 영역(전방 0.45~1.0, |횡|<0.3, z≥0.06) 점: 있는 프레임 %d개 (%.1f%%), 점 합 %d, 프레임당 최대 %d'
      % (nf, DUR, sum(1 for c in per if c), 100.0 * sum(1 for c in per if c) / max(nf, 1), sum(per), max(per) if per else 0))
if hits:
    H = np.array([h[1:] for h in hits])
    print('  전방 %.2f~%.2f, 횡 %+.2f~%+.2f, z %.3f~%.3f (중앙 %.3f), 카메라 거리 %.2f~%.2f (중앙 %.2f)'
          % (H[:, 0].min(), H[:, 0].max(), H[:, 1].min(), H[:, 1].max(), H[:, 2].min(), H[:, 2].max(), np.median(H[:, 2]), H[:, 3].min(), H[:, 3].max(), np.median(H[:, 3])))
    ed = [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 1.0]
    print('  카메라 거리 히스토그램: ' + ', '.join('%.1f~%.1f: %d' % (ed[i], ed[i+1], int(((H[:, 3] >= ed[i]) & (H[:, 3] < ed[i+1])).sum())) for i in range(len(ed) - 1)))
    from collections import Counter
    cc = Counter((round(h[1] / 0.05) * 0.05, round(h[2] / 0.05) * 0.05) for h in hits)
    print('  5 cm 셀별 등장 수 상위: ' + ', '.join('(%.2f,%+.2f)×%d' % (a, b, c) for (a, b), c in cc.most_common(6)))
    print('  → 1점이라도 있으면 mark_threshold 0 인 STVL 이 30 s 동안 LETHAL 로 둔다')
else:
    print('  없음 → 정지 상태의 정면 바닥에는 잡음 점이 없다')
