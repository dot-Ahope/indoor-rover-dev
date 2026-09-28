#!/usr/bin/env python3
"""f0a3 판정 보조 (2026-09-28 §14): bag 에서
  ① H1 — 복귀 구간(방향 |yaw|>120°) 상자 옆(map x 0.95~1.45)에서 로컬 코스트맵 LETHAL ↔ 패딩 풋프린트(0.26×0.175) 최소 거리(프레임별)
  ② V3 — /imu/data·/odometry/filtered 평균 발행률. 인자: BAG"""
import sys, math, bisect
import numpy as np
import rosbag2_py
from rclpy.serialization import deserialize_message
from rosidl_runtime_py.utilities import get_message


def yaw(q): return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))


BAG = sys.argv[1]
r = rosbag2_py.SequentialReader(); r.open(rosbag2_py.StorageOptions(uri=BAG, storage_id='sqlite3'), rosbag2_py.ConverterOptions('cdr', 'cdr'))
types = {t.name: t.type for t in r.get_all_topics_and_types()}
ob, mo, lc = [], [], []; cnt = {'/imu/data': [], '/odometry/filtered': []}
while r.has_next():
    tp, data, ts = r.read_next(); t = ts * 1e-9
    if tp in cnt: cnt[tp].append(t); continue
    if tp not in ('/tf', '/local_costmap/costmap'): continue
    m = deserialize_message(data, get_message(types[tp]))
    if tp == '/tf':
        for tr in m.transforms:
            p = (t, tr.transform.translation.x, tr.transform.translation.y, yaw(tr.transform.rotation))
            if tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link': ob.append(p)
            elif tr.header.frame_id == 'map' and tr.child_frame_id == 'odom': mo.append(p)
    else: lc.append((t, m))
for k, v in cnt.items():
    if len(v) > 1: print('V3: %s %.1f Hz (%d 개, %.0f s)' % (k, (len(v) - 1) / (v[-1] - v[0]), len(v), v[-1] - v[0]))


def last(arr, t):
    k = bisect.bisect_right([a[0] for a in arr], t) - 1; return arr[max(k, 0)]


FP = (0.26, 0.175); rows = []
for t, g in lc:
    _, x, y, th = last(ob, t); _, mx, my, mth = last(mo, t)
    c0, s0 = math.cos(mth), math.sin(mth); X, Y, TH = mx + c0 * x - s0 * y, my + s0 * x + c0 * y, th + mth
    if abs(math.degrees(math.atan2(math.sin(TH), math.cos(TH)))) < 120 or not (0.95 <= X <= 1.45): continue
    d = np.asarray(g.data, dtype=np.int16).reshape(g.info.height, g.info.width); iy, ix = np.nonzero(d >= 100)
    px = g.info.origin.position.x + (ix + 0.5) * g.info.resolution - x; py = g.info.origin.position.y + (iy + 0.5) * g.info.resolution - y
    c, s = math.cos(th), math.sin(th); bx, by = c * px + s * py, -s * px + c * py
    dist = np.hypot(np.maximum(np.abs(bx) - FP[0], 0), np.maximum(np.abs(by) - FP[1], 0))
    k = int(np.argmin(dist)); rows.append((X, Y, dist[k], bx[k], by[k]))
if rows:
    for X, Y, dd, bx, by in rows: print('  map (%.2f, %.3f) | 패딩 풋프린트↔LETHAL %.3f m @차체(%+.2f, %+.2f)' % (X, Y, dd, bx, by))
    print('H1: 복귀 상자 옆 로컬 여유 최소 %.3f m (프레임 %d)' % (min(r[2] for r in rows), len(rows)))
