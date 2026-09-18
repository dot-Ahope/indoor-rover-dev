#!/usr/bin/env python3
"""출발 직전 로버 뒤쪽 라이다 점 비교 (2026-09-18 dy3 '뒤 5 cm 물체' 검증). 인자: BAG GOAL_EPOCH [...]
  t −2~0 s 스캔들을 모아 base_link(보정 TF: yaw π−0.04677, x 0.152)로. 뒤쪽 구역 x < −0.20, |y| < 0.6 의 점을
  x 구간별로 요약(가장 가까운 점 무리의 x·y 범위·점 수·스캔마다 보인 비율 = 지속성), 그리고 빔 각도(라이다 원시각)도 같이.
  같은 물체가 다른 주행에서 더 멀리 보이면 → 배치 차이(실물). 원시각이 특정 빔에 몰리고 거리 일정 → 자기 몸체/오측정 의심.
"""
import sys, math
import numpy as np
import rosbag2_py
from rclpy.serialization import deserialize_message
from sensor_msgs.msg import LaserScan
LYAW, LX = math.pi - 0.04677, 0.152
a = sys.argv[1:]
for k in range(0, len(a), 2):
    bag, G = a[k], float(a[k + 1]); name = bag.split('_')[-1]
    r = rosbag2_py.SequentialReader(); r.open(rosbag2_py.StorageOptions(uri=bag, storage_id='sqlite3'), rosbag2_py.ConverterOptions('', ''))
    P = []; ns = 0
    while r.has_next():
        topic, data, ts = r.read_next(); t = ts * 1e-9 - G
        if topic != '/scan' or not (-2.0 < t < 0.0):
            continue
        sc = deserialize_message(data, LaserScan); ns += 1
        rr = np.asarray(sc.ranges, dtype=np.float64); aa = sc.angle_min + np.arange(rr.size) * sc.angle_increment
        ok = np.isfinite(rr) & (rr > sc.range_min) & (rr < 3.0)
        bx = LX + rr[ok] * np.cos(aa[ok] + LYAW); by = rr[ok] * np.sin(aa[ok] + LYAW)
        for x, y, ang, rg in zip(bx, by, np.degrees(aa[ok]), rr[ok]):
            if x < -0.20 and abs(y) < 0.6:
                P.append((ns, x, y, ang, rg))
    P = np.array(P) if P else np.zeros((0, 5))
    print('==== %s: 스캔 %d 장 (t −2~0 s), 뒤쪽 구역 점 %d 개' % (name, ns, len(P)))
    if not len(P):
        continue
    for lo, hi in ((-0.35, -0.20), (-0.50, -0.35), (-0.80, -0.50), (-1.20, -0.80), (-2.0, -1.2), (-3.2, -2.0)):
        s = (P[:, 1] >= lo) & (P[:, 1] < hi)
        if s.any():
            Q = P[s]; persist = len(set(Q[:, 0].astype(int))) / ns
            print('   x %+.2f~%+.2f: 점 %4d (스캔당 %.1f, 보인 스캔 %.0f%%) | y %+.2f~%+.2f | 라이다 원시각 %+.1f~%+.1f° | 거리 %.3f~%.3f m' % (
                lo, hi, s.sum(), s.sum() / ns, 100 * persist, Q[:, 2].min(), Q[:, 2].max(), Q[:, 3].min(), Q[:, 3].max(), Q[:, 4].min(), Q[:, 4].max()))
