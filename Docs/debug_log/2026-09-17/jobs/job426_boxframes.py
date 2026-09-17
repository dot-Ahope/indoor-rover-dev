#!/usr/bin/env python3
"""로컬(odom) vs 전역(map) 코스트맵의 상자 위치 비교 (2026-09-17 §15). 로버는 움직이지 않는다. 인자: BAG GOAL_EPOCH
  로컬 코스트맵 LETHAL 상자 셀(odom 영역 x 0.9~1.6, y −0.35~+0.25)을 그 시각 map->odom 으로 map 에 옮겨,
  가장 가까운 시각의 전역 코스트맵 상자 셀(map 같은 영역)과 좌측 끝 y·중심 y 비교. + map->odom 과 로버 map/odom 자세.
"""
import sys, math, bisect
import numpy as np
import rosbag2_py
from rclpy.serialization import deserialize_message
from tf2_msgs.msg import TFMessage
from nav_msgs.msg import OccupancyGrid

BAG, G = sys.argv[1], float(sys.argv[2])


def yaw_of(q):
    return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))


r = rosbag2_py.SequentialReader(); r.open(rosbag2_py.StorageOptions(uri=BAG, storage_id='sqlite3'), rosbag2_py.ConverterOptions('', ''))
lcs, gcs, mo, ob = [], [], [], []
while r.has_next():
    topic, data, ts = r.read_next(); t = ts * 1e-9 - G
    if topic == '/local_costmap/costmap' and -1 < t < 32:
        lcs.append(deserialize_message(data, OccupancyGrid))
    elif topic == '/global_costmap/costmap' and -1 < t < 32:
        gcs.append(deserialize_message(data, OccupancyGrid))
    elif topic == '/tf':
        for tr in deserialize_message(data, TFMessage).transforms:
            st = tr.header.stamp.sec + tr.header.stamp.nanosec * 1e-9 - G
            if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom':
                mo.append((st, tr.transform.translation.x, tr.transform.translation.y, yaw_of(tr.transform.rotation)))
            elif tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link':
                ob.append((st, tr.transform.translation.x, tr.transform.translation.y, yaw_of(tr.transform.rotation)))
mo.sort(); ob.sort(); mot = [m[0] for m in mo]; obt = [o[0] for o in ob]


def near(seq, ts, t):
    k = min(max(bisect.bisect_left(ts, t), 0), len(seq) - 1)
    if k > 0 and abs(ts[k - 1] - t) < abs(ts[k] - t):
        k -= 1
    return seq[k]


def stamp(m):
    return m.header.stamp.sec + m.header.stamp.nanosec * 1e-9 - G


def box_cells(m, xr, yr):
    d = np.array(m.data, dtype=np.int16).reshape(m.info.height, m.info.width); jj, ii = np.where(d >= 100)
    X = m.info.origin.position.x + (ii + 0.5) * m.info.resolution; Y = m.info.origin.position.y + (jj + 0.5) * m.info.resolution
    s = (X > xr[0]) & (X < xr[1]) & (Y > yr[0]) & (Y < yr[1])
    return X[s], Y[s]


gst = [stamp(g) for g in gcs]
print('==== %s ====' % BAG.split('_')[-1])
print('   t   | map->odom dx     dy    dyaw | 로버 odom (x, y, yaw)   → map (x, y) | 로컬 상자→map: y 범위(셀중심)  중심 | 전역 상자: y 범위   중심 | 좌측끝 차(로컬−전역)')
last = -9
for m in lcs:
    t = stamp(m)
    if t - last < 2.4:
        continue
    last = t
    _, ax, ay, ath = near(mo, mot, t); _, px, py, pth = near(ob, obt, t)
    mx, my = ax + px * math.cos(ath) - py * math.sin(ath), ay + px * math.sin(ath) + py * math.cos(ath)
    X, Y = box_cells(m, (0.9, 1.6), (-0.35, 0.25))
    g = gcs[int(np.argmin([abs(s - t) for s in gst]))]
    if X.size:
        MX = ax + X * math.cos(ath) - Y * math.sin(ath); MY = ay + X * math.sin(ath) + Y * math.cos(ath)
        sel = (MX > 0.9) & (MX < 1.6)
        lo, hi, cen = MY[sel].min(), MY[sel].max(), MY[sel].mean()
    else:
        lo = hi = cen = float('nan')
    GX, GY = box_cells(g, (0.9, 1.6), (-0.35, 0.25))
    glo, ghi, gcen = (GY.min(), GY.max(), GY.mean()) if GY.size else (float('nan'),) * 3
    print(' %5.1f | %+6.3f %+6.3f %+5.2f° | (%.3f, %+.3f, %+5.1f°) → (%.3f, %+.3f) | %+.3f~%+.3f %+.3f (%2d) | %+.3f~%+.3f %+.3f (%2d) | %+.3f' % (
        t, ax, ay, math.degrees(ath), px, py, math.degrees(pth), mx, my, lo, hi, cen, X.size, glo, ghi, gcen, GY.size, hi - ghi))
