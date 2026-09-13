#!/usr/bin/env python3
"""정지 상태에서 깊이 점군을 8 s 표본해 '단독 셀' 의 출처를 본다 (2026-09-11). 로버는 움직이지 않는다.

  job304/305: v5 정체를 만든 LETHAL 은 라이다 근거 없는 1셀짜리(상자 좌측 가장자리 옆, 통로 안)였고,
  전역에도 같은 종류의 1셀이 좌측에 생겨 계획을 상자 쪽으로 밀었다. 깊이 점군에서
    - 통로 띠(차체좌표 횡 +0.15~+0.70, 전방 0.6~1.8, z ≥ min_obstacle_height 0.06) 에 점이 있는가, 얼마나 자주(프레임 비율)
    - 그 점들이 고립점(0.05 m 안에 이웃 ≤ 2)인가 — 스테레오 경계 비산점(flying pixel) 의 특징
    - 상자 점군의 z 분포(상자 높이), 좌측 띠(횡 +0.7~+1.3)의 z 분포(낮은 물체인가)
  를 센다. 좌표는 tf 로 base_link 로 옮긴다.
"""
import sys, math, time
import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import PointCloud2, LaserScan
from sensor_msgs_py import point_cloud2 as pc2
import tf2_ros

DUR = float(sys.argv[1]) if len(sys.argv) > 1 else 8.0
TOPIC = '/camera/camera/depth/color/points'
MIN_H = 0.06
rclpy.init()
n = Node('depth306')
buf = tf2_ros.Buffer(); tl = tf2_ros.TransformListener(buf, n)
frames = []; scans = []
n.create_subscription(PointCloud2, TOPIC, lambda m: frames.append(m), qos_profile_sensor_data)
n.create_subscription(LaserScan, '/scan', lambda m: scans.append(m), qos_profile_sensor_data)
t0 = time.time()
while time.time() - t0 < DUR + 2.0:
    rclpy.spin_once(n, timeout_sec=0.05)
    if time.time() - t0 > 2.0 and len(frames) == 0 and int(time.time() - t0) == 2:
        pass
print('깊이 프레임 %d개 (%.1f s), 스캔 %d개' % (len(frames), DUR + 2.0, len(scans)))
if not frames:
    print('점군 없음 — 토픽 %s 확인' % TOPIC); sys.exit(1)
fr = frames[0].header.frame_id
try:
    tr = buf.lookup_transform('base_link', fr, rclpy.time.Time(), timeout=rclpy.duration.Duration(seconds=3.0)).transform
except Exception as e:
    print('TF 실패 %s->base_link: %s' % (fr, e)); sys.exit(1)
q = tr.rotation
R = np.array([[1 - 2 * (q.y * q.y + q.z * q.z), 2 * (q.x * q.y - q.z * q.w), 2 * (q.x * q.z + q.y * q.w)],
              [2 * (q.x * q.y + q.z * q.w), 1 - 2 * (q.x * q.x + q.z * q.z), 2 * (q.y * q.z - q.x * q.w)],
              [2 * (q.x * q.z - q.y * q.w), 2 * (q.y * q.z + q.x * q.w), 1 - 2 * (q.x * q.x + q.y * q.y)]])
T = np.array([tr.translation.x, tr.translation.y, tr.translation.z])
print('점군 프레임 %s -> base_link: t=(%.3f, %.3f, %.3f)' % (fr, T[0], T[1], T[2]))

band_cnt = []; iso_cnt = []; iso_pts = []; band_pts = []
box_z = []; left_z = []; left_xy = []; box_xy = []; floor_z = []
tot = []
for k, m in enumerate(frames[:int(DUR * 30)]):
    pts = pc2.read_points_numpy(m, field_names=('x', 'y', 'z'), skip_nans=True)
    if len(pts) == 0:
        band_cnt.append(0); iso_cnt.append(0); tot.append(0); continue
    P = pts @ R.T + T
    tot.append(len(P))
    x, y, z = P[:, 0], P[:, 1], P[:, 2]
    # 바닥 높이 표본 (전방 0.6~1.0, 횡 ±0.2 의 z 하위 분포)
    fm = (x > 0.6) & (x < 1.0) & (np.abs(y) < 0.2)
    if fm.any():
        floor_z.append(np.percentile(z[fm], 10))
    band = (y > 0.15) & (y < 0.70) & (x > 0.6) & (x < 1.8) & (z >= MIN_H) & (z < 0.40)
    nb = int(band.sum()); band_cnt.append(nb)
    if nb:
        B = P[band]
        # 고립점: 같은 프레임의 (모든 z≥0.03 점) 중 0.05 m 안 이웃 수 ≤ 2
        Q = P[(z >= 0.03) & (x > 0.4) & (x < 2.0) & (np.abs(y) < 1.5)]
        iso = 0
        for p in B:
            d = np.hypot(Q[:, 0] - p[0], Q[:, 1] - p[1])
            nn = int(((d < 0.05) & (np.abs(Q[:, 2] - p[2]) < 0.05)).sum()) - 1
            if nn <= 2:
                iso += 1; iso_pts.append((k, p[0], p[1], p[2], nn))
        iso_cnt.append(iso); band_pts.extend(B.tolist())
    else:
        iso_cnt.append(0)
    bm = (x > 1.0) & (x < 2.0) & (y > -0.35) & (y < 0.15) & (z >= MIN_H)
    if bm.any():
        box_z.extend(z[bm].tolist()); box_xy.extend(P[bm][:, :2].tolist())
    lm = (x > 0.0) & (x < 1.8) & (y > 0.70) & (y < 1.35) & (z >= MIN_H) & (z < 0.40)
    if lm.any():
        left_z.extend(z[lm].tolist()); left_xy.extend(P[lm][:, :2].tolist())
nfr = len(tot)
print('프레임당 점 수 중앙값 %d' % int(np.median(tot)))
if floor_z:
    print('바닥 z(전방 0.6~1.0 하위 10%%) 중앙값 %+.3f  (min_obstacle_height %.2f)' % (np.median(floor_z), MIN_H))
print('통로 띠(횡 +0.15~+0.70, 전방 0.6~1.8, z≥%.2f) 점: 프레임 %d개 중 점 있는 프레임 %d개 (%.0f%%), 프레임당 최대 %d, 합 %d'
      % (MIN_H, nfr, sum(1 for c in band_cnt if c), 100.0 * sum(1 for c in band_cnt if c) / max(nfr, 1), max(band_cnt) if band_cnt else 0, sum(band_cnt)))
print('  그중 고립점(0.05 m 이웃 ≤2): %d개 (%.0f%%)' % (sum(iso_cnt), 100.0 * sum(iso_cnt) / max(sum(band_cnt), 1)))
if band_pts:
    B = np.array(band_pts)
    print('  띠 점 위치: 전방 %.2f~%.2f, 횡 %+.2f~%+.2f, z %.3f~%.3f (z 중앙 %.3f)' % (B[:, 0].min(), B[:, 0].max(), B[:, 1].min(), B[:, 1].max(), B[:, 2].min(), B[:, 2].max(), np.median(B[:, 2])))
    # 5 cm 셀로 묶어 어느 셀에 몇 번 나타났는지
    from collections import Counter
    cc = Counter((round(p[0] / 0.05) * 0.05, round(p[1] / 0.05) * 0.05) for p in band_pts)
    print('  띠 점이 든 5 cm 셀 %d개, 상위: %s' % (len(cc), ', '.join('(%.2f,%+.2f)×%d' % (a, b, c) for (a, b), c in cc.most_common(8))))
if iso_pts:
    print('  고립점 예 (프레임, 전방, 횡, z, 이웃수):')
    for r in iso_pts[:12]:
        print('    f%03d  %.2f %+.2f z %.3f  이웃 %d' % r)
if box_z:
    bz = np.array(box_z); bxy = np.array(box_xy)
    print('상자 영역(전방 1.0~2.0, 횡 -0.35~+0.15) 점 %d: z 5%% %.3f 50%% %.3f 95%% %.3f | 전방 %.2f~%.2f 횡 %+.2f~%+.2f (5~95%%)'
          % (len(bz), np.percentile(bz, 5), np.percentile(bz, 50), np.percentile(bz, 95), np.percentile(bxy[:, 0], 5), np.percentile(bxy[:, 0], 95), np.percentile(bxy[:, 1], 5), np.percentile(bxy[:, 1], 95)))
if left_z:
    lz = np.array(left_z); lxy = np.array(left_xy)
    print('좌측 띠(횡 +0.70~+1.35, 전방 0~1.8) 점 %d (프레임당 %.0f): z 5%% %.3f 50%% %.3f 95%% %.3f | 전방 %.2f~%.2f 횡 %+.2f~%+.2f (5~95%%)'
          % (len(lz), len(lz) / max(nfr, 1), np.percentile(lz, 5), np.percentile(lz, 50), np.percentile(lz, 95), np.percentile(lxy[:, 0], 5), np.percentile(lxy[:, 0], 95), np.percentile(lxy[:, 1], 5), np.percentile(lxy[:, 1], 95)))
    hist, edges = np.histogram(lz, bins=[0.06, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40])
    print('  좌측 띠 z 히스토그램: ' + ', '.join('%.2f~%.2f: %d' % (edges[i], edges[i + 1], hist[i]) for i in range(len(hist))))
    hist2, e2 = np.histogram(lxy[:, 1], bins=np.arange(0.70, 1.40, 0.10))
    print('  좌측 띠 횡 히스토그램: ' + ', '.join('%+.2f~%+.2f: %d' % (e2[i], e2[i + 1], hist2[i]) for i in range(len(hist2))))
# 라이다: 좌측 물체 위치 (base_link, 최신 스캔 5개 평균 아님 — 마지막 스캔)
if scans:
    s = scans[-1]
    try:
        lt = buf.lookup_transform('base_link', s.header.frame_id, rclpy.time.Time()).transform
        lq = lt.rotation; lyaw = math.atan2(2 * (lq.w * lq.z + lq.x * lq.y), 1 - 2 * (lq.y * lq.y + lq.z * lq.z))
        rr = np.array(s.ranges); ang = s.angle_min + np.arange(len(rr)) * s.angle_increment
        ok = np.isfinite(rr) & (rr > s.range_min) & (rr < s.range_max)
        lx = rr[ok] * np.cos(ang[ok]); ly = rr[ok] * np.sin(ang[ok])
        bx = lt.translation.x + lx * math.cos(lyaw) - ly * math.sin(lyaw); by = lt.translation.y + lx * math.sin(lyaw) + ly * math.cos(lyaw)
        print('라이다(z %.3f) 좌측 점: 전방 띠별 최소 횡' % lt.translation.z)
        for lo in np.arange(-0.4, 1.8, 0.2):
            m = (bx >= lo) & (bx < lo + 0.2) & (by > 0.3) & (by < 1.6)
            print('    전방 %+.1f~%+.1f: %s' % (lo, lo + 0.2, ('최소 횡 %+.2f, 점 %d' % (by[m].min(), m.sum())) if m.any() else '점 없음'))
        m = (bx > 0.9) & (bx < 1.9) & (by > -0.5) & (by < 0.3)
        print('  라이다 전방 0.9~1.9 횡 -0.5~+0.3 (상자 자리) 점 %d개 → %s' % (m.sum(), '라이다가 상자를 본다' if m.sum() > 5 else '라이다는 상자를 못 본다(라이다 높이 아래)'))
    except Exception as e:
        print('라이다 TF 실패: %s' % e)
