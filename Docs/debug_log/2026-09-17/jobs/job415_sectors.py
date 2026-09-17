#!/usr/bin/env python3
"""출발 자세 비교(빠른 판정, 2026-09-17): 현재 스캔 vs bag 출발 스캔의 전/후/좌/우 좁은 복도(폭 ±4 cm) 최근접 거리.
   전후 거리 차 = 로버 x 변위(요 같다고 가정), 좌우 차 = y 변위. 상자는 라이다 높이에 안 보이므로 방 기준 변위다. 인자: BAG NOW_NPY
"""
import sys, math
import numpy as np
import rosbag2_py
from rclpy.serialization import deserialize_message
from sensor_msgs.msg import LaserScan
LX, LYAW = 0.152, math.pi


def to_base(amin, ainc, ranges):
    r = np.asarray(ranges, dtype=np.float64); a = amin + np.arange(r.size) * ainc
    ok = np.isfinite(r) & (r > 0.25) & (r < 8.0)
    px, py = r[ok] * np.cos(a[ok]), r[ok] * np.sin(a[ok])
    return np.stack([LX + px * math.cos(LYAW) - py * math.sin(LYAW), py * math.cos(LYAW) + px * math.sin(LYAW)], 1)


def corridors(P):
    out = {}
    for name, sel, key in (('전방', (np.abs(P[:, 1]) < 0.04) & (P[:, 0] > 0.3), 0), ('후방', (np.abs(P[:, 1]) < 0.04) & (P[:, 0] < -0.3), 0),
                           ('좌', (np.abs(P[:, 0]) < 0.04) & (P[:, 1] > 0.2), 1), ('우', (np.abs(P[:, 0]) < 0.04) & (P[:, 1] < -0.2), 1)):
        v = np.abs(P[sel, key]); out[name] = float(np.percentile(v, 10)) if v.size >= 3 else float('nan')
    # 요 추정: 전방 ±1.5 m 안 가장 긴 벽의 기울기는 생략 — 좌/우 복도 여러 x 위치의 거리 기울기로 대신
    return out


r = rosbag2_py.SequentialReader(); r.open(rosbag2_py.StorageOptions(uri=sys.argv[1], storage_id='sqlite3'), rosbag2_py.ConverterOptions('', ''))
refs = []
while r.has_next() and len(refs) < 25:
    topic, data, ts = r.read_next()
    if topic == '/scan':
        m = deserialize_message(data, LaserScan); refs.append(corridors(to_base(m.angle_min, m.angle_increment, m.ranges)))
ref = {k: float(np.nanmedian([d[k] for d in refs[5:25]])) for k in refs[0]}
v = np.load(sys.argv[2]); cur = corridors(to_base(v[0], v[1], v[2:]))
print('복도 최근접 (10 %% 분위, m)   %s' % '  '.join('%s' % k for k in ref))
print('  bag 출발: %s' % '  '.join('%.3f' % ref[k] for k in ref))
print('  현재    : %s' % '  '.join('%.3f' % cur[k] for k in ref))
print('  차(현재−bag): %s' % '  '.join('%+.3f' % (cur[k] - ref[k]) for k in ref))
print('  → x 변위 추정: 전방으로 %+.3f m (전방 거리 감소 %+.3f, 후방 거리 증가 %+.3f 평균)' % (((ref['전방'] - cur['전방']) + (cur['후방'] - ref['후방'])) / 2, ref['전방'] - cur['전방'], cur['후방'] - ref['후방']))
