#!/usr/bin/env python3
"""상자 좌측 가장자리 '연장 셀' 의 출처 (2026-09-14). 로버는 움직이지 않는다.

  inf2 bag: 코스트맵 상자 셀은 횡 +0.21·전진 1.59 까지인데 깊이 5~95 % 가장자리는 +0.09·전진 1.24 였다.
  정지 상태 20 s 표본으로 상자 주변 깊이점을 띠별로 센다:
    핵심(상자 본체)     : 전진 [BX−0.05, BX+0.15], 횡 [BY−0.12, BY+0.12], z ≥ 0.06
    좌측 연장 띠(의심)  : 전진 [BX−0.05, BX+0.50], 횡 [BY+0.12, BY+0.35], z ≥ 0.06
    뒤쪽 연장 띠(의심)  : 전진 [BX+0.15, BX+0.50], 횡 [BY−0.12, BY+0.12], z ≥ 0.06
  각 띠: 점 있는 프레임 비율, 프레임당 점 수(중앙/최대), z 분포, 고립 비율(같은 프레임 5 cm 안 이웃 ≤2),
        그리고 그 점들이 카메라→상자 가장자리 방향 광선 위에 있는지(혼합 화소 특징: 가장자리 방위각 ±1° 안, 거리는 상자보다 멀다).
  또 같은 시각 로컬/전역 코스트맵의 상자 LETHAL 범위를 찍어 깊이점 범위와 비교한다.
  인자: BX BY (상자 전면 x, 중심 y, 차체좌표; 기본 job248 결과를 넣는다) [DUR=20]
"""
import sys, math, time
import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data, QoSProfile, DurabilityPolicy, ReliabilityPolicy
from sensor_msgs.msg import PointCloud2
from nav_msgs.msg import OccupancyGrid
from sensor_msgs_py import point_cloud2 as pc2
import tf2_ros

BX = float(sys.argv[1]); BY = float(sys.argv[2]); DUR = float(sys.argv[3]) if len(sys.argv) > 3 else 20.0
rclpy.init(); n = Node('edge312'); buf = tf2_ros.Buffer(); tl = tf2_ros.TransformListener(buf, n)
F = []; G = {}
qos_tl = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL, reliability=ReliabilityPolicy.RELIABLE)
n.create_subscription(PointCloud2, __import__('os').environ.get('TOPIC', '/camera/camera/depth/color/points'), lambda m: F.append(m), qos_profile_sensor_data)
n.create_subscription(OccupancyGrid, '/local_costmap/costmap', lambda m: G.__setitem__('lc', m), qos_tl)
n.create_subscription(OccupancyGrid, '/global_costmap/costmap', lambda m: G.__setitem__('gc', m), qos_tl)
t0 = time.time()
while time.time() - t0 < DUR:
    rclpy.spin_once(n, timeout_sec=0.05)
tr = buf.lookup_transform('base_link', F[0].header.frame_id, rclpy.time.Time(), timeout=rclpy.duration.Duration(seconds=3.0)).transform
q = tr.rotation
R = np.array([[1-2*(q.y*q.y+q.z*q.z), 2*(q.x*q.y-q.z*q.w), 2*(q.x*q.z+q.y*q.w)],[2*(q.x*q.y+q.z*q.w), 1-2*(q.x*q.x+q.z*q.z), 2*(q.y*q.z-q.x*q.w)],[2*(q.x*q.z-q.y*q.w), 2*(q.y*q.z+q.x*q.w), 1-2*(q.x*q.x+q.y*q.y)]])
T = np.array([tr.translation.x, tr.translation.y, tr.translation.z])
CAM = T[:2]
bands = {
    '핵심(본체)': ((BX - 0.05, BX + 0.15), (BY - 0.12, BY + 0.12)),
    '좌측 연장': ((BX - 0.05, BX + 0.50), (BY + 0.12, BY + 0.35)),
    '뒤쪽 연장': ((BX + 0.15, BX + 0.50), (BY - 0.12, BY + 0.12)),
    '우측 연장': ((BX - 0.05, BX + 0.50), (BY - 0.35, BY - 0.12)),
    '앞쪽 연장': ((BX - 0.20, BX - 0.05), (BY - 0.12, BY + 0.12)),   # inf4: 코스트맵 상자가 전면보다 0.13 앞까지 켜짐
}
ZTH = float(__import__('os').environ.get('ZTH', '0.08'))   # min_obstacle_height 후보 — 이 아래 점 비율을 띠별로 센다
stats = {k: dict(frames=0, counts=[], z=[], x=[], y=[], iso=0, tot=0, onray=0) for k in bands}
edge_az = math.atan2(BY + 0.09 - CAM[1], BX - CAM[0])   # 카메라에서 본 상자 좌측 앞 모서리 방위
edge_r = math.hypot(BX - CAM[0], BY + 0.09 - CAM[1])
nf = 0
for m in F:
    P = pc2.read_points_numpy(m, field_names=('x', 'y', 'z'), skip_nans=True) @ R.T + T
    nf += 1
    x, y, z = P[:, 0], P[:, 1], P[:, 2]
    Q = P[(z >= 0.03) & (x > 0.5) & (x < 2.2) & (np.abs(y) < 1.0)]
    for k, ((x0, x1), (y0, y1)) in bands.items():
        sel = (x >= x0) & (x < x1) & (y >= y0) & (y < y1) & (z >= 0.06) & (z < 0.40)
        c = int(sel.sum()); s = stats[k]; s['counts'].append(c)
        if c:
            s['frames'] += 1; B = P[sel]
            s['z'].extend(B[:, 2].tolist()); s['x'].extend(B[:, 0].tolist()); s['y'].extend(B[:, 1].tolist())
            for p in B[:200]:
                d = np.hypot(Q[:, 0] - p[0], Q[:, 1] - p[1]); nn = int(((d < 0.05) & (np.abs(Q[:, 2] - p[2]) < 0.05)).sum()) - 1
                s['tot'] += 1
                if nn <= 2: s['iso'] += 1
                az = math.atan2(p[1] - CAM[1], p[0] - CAM[0]); rr = math.hypot(p[0] - CAM[0], p[1] - CAM[1])
                if abs(az - edge_az) < math.radians(1.5) and rr > edge_r: s['onray'] += 1
print('프레임 %d (%.0f s). 상자 전면 x %.2f 중심 y %+.2f (입력). 카메라 (%.3f, %.3f). 좌측 앞 모서리 방위 %+.1f°, 거리 %.2f'
      % (nf, DUR, BX, BY, CAM[0], CAM[1], math.degrees(edge_az), edge_r))
print('  띠          프레임비율  점/프레임(중앙/최대)  z 5~50~95%%         x 5~95%%       y 5~95%%       고립%%   모서리광선%%')
for k, s in stats.items():
    if s['frames'] == 0:
        print('  %-10s   0%%' % k); continue
    z = np.array(s['z']); x = np.array(s['x']); y = np.array(s['y']); c = np.array(s['counts'])
    print('  %-10s %4.0f%%     %4d / %4d        %.3f %.3f %.3f   %.2f~%.2f   %+.2f~%+.2f   %3.0f%%    %3.0f%%   z<%.2f: %3.0f%%'
          % (k, 100.0 * s['frames'] / nf, int(np.median(c[c > 0])), c.max(), np.percentile(z, 5), np.percentile(z, 50), np.percentile(z, 95),
             np.percentile(x, 5), np.percentile(x, 95), np.percentile(y, 5), np.percentile(y, 95),
             100.0 * s['iso'] / max(s['tot'], 1), 100.0 * s['onray'] / max(s['tot'], 1), ZTH, 100.0 * float((z < ZTH).mean())))
    # ZTH 를 적용하면 이 띠에서 프레임당 남는 점 수 (min_obstacle_height 후보 평가)
    keep = [float((np.array(s['z'][sum(c[:i]):sum(c[:i + 1])]) >= ZTH).sum()) for i in range(len(c)) if c[i] > 0] if False else None
    z_hi = (z >= ZTH).sum()
    print('             → z≥%.2f 인 점 %d / %d (프레임당 평균 %.1f)' % (ZTH, z_hi, len(z), z_hi / max(nf, 1)))
# 코스트맵 상자 범위 (차체좌표)
for key, name in (('lc', '로컬'), ('gc', '전역')):
    g = G.get(key)
    if not g:
        print('%s 코스트맵 없음' % name); continue
    try:
        t = buf.lookup_transform(g.header.frame_id, 'base_link', rclpy.time.Time()).transform
    except Exception as e:
        print('%s TF 실패 %s' % (name, e)); continue
    qq = t.rotation; yaw = math.atan2(2*(qq.w*qq.z+qq.x*qq.y), 1-2*(qq.y*qq.y+qq.z*qq.z))
    d = np.array(g.data, dtype=np.int16).reshape(g.info.height, g.info.width)
    jj, ii = np.where(d >= 100)
    X = g.info.origin.position.x + (ii + 0.5) * g.info.resolution; Y = g.info.origin.position.y + (jj + 0.5) * g.info.resolution
    dx, dy = X - t.translation.x, Y - t.translation.y
    bx = dx * math.cos(yaw) + dy * math.sin(yaw); by = -dx * math.sin(yaw) + dy * math.cos(yaw)
    sel = (bx > BX - 0.15) & (bx < BX + 0.6) & (by > BY - 0.4) & (by < BY + 0.4)
    if sel.any():
        print('%s 코스트맵 상자 근방 LETHAL %d셀: x %.2f~%.2f, y %+.2f~%+.2f  (깊이 본체 대비 좌측 +%.2f, 뒤쪽 +%.2f 연장)'
              % (name, sel.sum(), bx[sel].min(), bx[sel].max(), by[sel].min(), by[sel].max(), by[sel].max() - (BY + 0.09), bx[sel].max() - (BX + 0.11)))
        ys = sorted(set(np.round(by[sel] / 0.05).astype(int)))
        print('   y 열별 셀 수: ' + ', '.join('%+.2f:%d' % (yy * 0.05, int((np.round(by[sel] / 0.05).astype(int) == yy).sum())) for yy in ys))
    else:
        print('%s 코스트맵 상자 근방 LETHAL 없음' % name)
