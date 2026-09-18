#!/usr/bin/env python3
"""라이다가 상자를 보는가 (2026-09-18, 사용자 질의). 인자: BAG GOAL_EPOCH BOX_FX BOX_CY
  출발 전 t −2~0 s 스캔을 base_link 로(보정 yaw π−0.04677, x 0.152) — prep 상자 자리(전면 FX~FX+0.11, 중심 CY±0.09) ±5 cm 안 점 수.
"""
import sys, math
import numpy as np
import rosbag2_py
from rclpy.serialization import deserialize_message
from sensor_msgs.msg import LaserScan
LYAW, LX = math.pi - 0.04677, 0.152
bag, G, fx, cy = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4])
r = rosbag2_py.SequentialReader(); r.open(rosbag2_py.StorageOptions(uri=bag, storage_id='sqlite3'), rosbag2_py.ConverterOptions('', ''))
ns = hit = 0; near = []
while r.has_next():
    topic, data, ts = r.read_next(); t = ts * 1e-9 - G
    if topic != '/scan' or not (-2.0 < t < 0.0):
        continue
    sc = deserialize_message(data, LaserScan); ns += 1
    rr = np.asarray(sc.ranges, dtype=np.float64); aa = sc.angle_min + np.arange(rr.size) * sc.angle_increment
    ok = np.isfinite(rr) & (rr > sc.range_min)
    x = LX + rr[ok] * np.cos(aa[ok] + LYAW); y = rr[ok] * np.sin(aa[ok] + LYAW)
    w = (x > fx - 0.05) & (x < fx + 0.16) & (y > cy - 0.14) & (y < cy + 0.14); hit += int(w.sum())
    f = (np.abs(y - cy) < 0.10) & (x > 0.3); near += list(x[f])
print('스캔 %d 장, 상자 자리(±5 cm) 라이다 점 %d 개(스캔당 %.1f)' % (ns, hit, hit / max(ns, 1)))
print('상자 중심선 y %+.2f±0.10 방향 라이다 점 x 분포(가까운 순 10): %s' % (cy, ' '.join('%.2f' % v for v in sorted(near)[:10])))
