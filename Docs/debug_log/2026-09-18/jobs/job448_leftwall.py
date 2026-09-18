#!/usr/bin/env python3
"""원경로 옆 위치가 회차마다 다른 이유 (2026-09-18 §15). 인자: NAME BAG GOAL_EPOCH [...]
  로버가 map x 1.20 에 닿은 시각 3 s 전의 /plan 과 그 시각 전역 코스트맵(map):
  - 상자 LETHAL 좌측 끝 y(x 1.0~1.4, y < 0.2), 왼쪽 LETHAL 가장 가까운 y(x 1.0~1.4, y > 0.2)
  - 둘 사이 통로 폭·중앙, 원경로 y(x 1.20) — 경로가 통로 중앙에서 상자 쪽으로 얼마나 치우쳤나
  - 같은 x 대에서 전역 코스트맵 비용(0~100) 단면 y 0.10~0.60 (5 cm 간격)
"""
import sys, math, bisect
import numpy as np
import rosbag2_py
from rclpy.serialization import deserialize_message
from tf2_msgs.msg import TFMessage
from nav_msgs.msg import OccupancyGrid, Path


def yaw_of(q):
    return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))


a = sys.argv[1:]
print('run | 상자 좌끝 y | 왼쪽 LETHAL y (x) | 통로 폭 | 통로 중앙 | 원경로 y@1.20 | 중앙−경로 | 비용 단면 y 0.10,0.15,...,0.60 (x 1.15~1.25 평균)')
for k in range(0, len(a), 3):
    name, bag, G = a[k], a[k + 1], float(a[k + 2])
    r = rosbag2_py.SequentialReader(); r.open(rosbag2_py.StorageOptions(uri=bag, storage_id='sqlite3'), rosbag2_py.ConverterOptions('', ''))
    ob, mo, gcs, plans = [], {}, [], []
    while r.has_next():
        topic, data, ts = r.read_next(); t = ts * 1e-9 - G
        if topic == '/tf':
            for tr in deserialize_message(data, TFMessage).transforms:
                st = tr.header.stamp.sec + tr.header.stamp.nanosec * 1e-9 - G
                v = (st, tr.transform.translation.x, tr.transform.translation.y, yaw_of(tr.transform.rotation))
                if tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link':
                    ob.append(v)
                elif tr.header.frame_id == 'map' and tr.child_frame_id == 'odom':
                    mo[round(st, 4)] = v
        elif topic == '/global_costmap/costmap' and -3 < t < 45:
            gcs.append((t, deserialize_message(data, OccupancyGrid)))
        elif topic == '/plan' and -1 < t < 45:
            m = deserialize_message(data, Path); plans.append((t, np.array([[p.pose.position.x, p.pose.position.y] for p in m.poses])))
    ob.sort(); mo = sorted(mo.values()); obt = [o[0] for o in ob]; mot = [m[0] for m in mo]

    def at(t):
        _, ox, oy, oth = ob[min(max(bisect.bisect_left(obt, t), 0), len(ob) - 1)]
        _, ax, ay, ath = mo[min(max(bisect.bisect_right(mot, t) - 1, 0), len(mo) - 1)]
        return (ax + ox * math.cos(ath) - oy * math.sin(ath), ay + ox * math.sin(ath) + oy * math.cos(ath))
    ta = next(t for t in np.arange(0, 40, 0.05) if at(t)[0] >= 1.20)
    gc = [g for g in gcs if g[0] <= ta][-1][1]; pl = [p for p in plans if p[0] <= ta - 3.0][-1][1]
    d = np.array(gc.data, dtype=np.int16).reshape(gc.info.height, gc.info.width); res = gc.info.resolution
    ox, oy = gc.info.origin.position.x, gc.info.origin.position.y
    jj, ii = np.where(d >= 100); X = ox + (ii + 0.5) * res; Y = oy + (jj + 0.5) * res
    bs = (X > 1.0) & (X < 1.4) & (Y < 0.2) & (Y > -0.4); ls = (X > 1.0) & (X < 1.4) & (Y > 0.2) & (Y < 1.5)
    by = Y[bs].max() + res / 2 if bs.any() else float('nan')
    ly = Y[ls].min() - res / 2 if ls.any() else float('nan'); lx = X[ls][np.argmin(Y[ls])] if ls.any() else float('nan')
    yp = float('nan')
    for q in range(len(pl) - 1):
        if (pl[q, 0] - 1.20) * (pl[q + 1, 0] - 1.20) <= 0 and pl[q, 0] != pl[q + 1, 0]:
            u = (1.20 - pl[q, 0]) / (pl[q + 1, 0] - pl[q, 0]); yp = pl[q, 1] + u * (pl[q + 1, 1] - pl[q, 1]); break
    prof = []
    for yy in np.arange(0.10, 0.601, 0.05):
        vals = []
        for xx in (1.15, 1.20, 1.25):
            i = int((xx - ox) / res); j = int((yy - oy) / res); vals.append(int(d[j, i]))
        prof.append('%3d' % round(np.mean(vals)))
    mid = (by + ly) / 2
    print('%s | %+.3f | %+.3f (%.2f) | %.3f | %+.3f | %+.3f | %+.3f | %s' % (name, by, ly, lx, ly - by, mid, yp, mid - yp, ' '.join(prof)))
