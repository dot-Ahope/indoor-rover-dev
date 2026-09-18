#!/usr/bin/env python3
"""출발 순간 로버 근처 장애물 셀 (2026-09-18 dy3: 출발 0.04 s 스무더 충돌·0.88 s Optimizer fail). 인자: BAG GOAL_EPOCH [BAG GOAL_EPOCH ...]
  t −3~+3 s 의 로컬·전역 코스트맵에서 차체 외곽(반길이 0.25·반폭 0.165) 0.30 m 안의 LETHAL/내접(99) 셀을 차체 좌표로,
  같은 시각 /scan 의 0.6 m 안 점(base_link, 보정 TF yaw π−0.04677·x 0.152)도.
"""
import sys, math, bisect
import numpy as np
import rosbag2_py
from rclpy.serialization import deserialize_message
from tf2_msgs.msg import TFMessage
from nav_msgs.msg import OccupancyGrid
from sensor_msgs.msg import LaserScan
HL, HW = 0.25, 0.165
LYAW, LX = math.pi - 0.04677, 0.152


def yaw_of(q):
    return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))


a = sys.argv[1:]
for k in range(0, len(a), 2):
    bag, G = a[k], float(a[k + 1]); name = bag.split('_')[-1]
    r = rosbag2_py.SequentialReader(); r.open(rosbag2_py.StorageOptions(uri=bag, storage_id='sqlite3'), rosbag2_py.ConverterOptions('', ''))
    ob, mo, cms, scans = [], [], [], []
    while r.has_next():
        topic, data, ts = r.read_next(); t = ts * 1e-9 - G
        if topic == '/tf':
            for tr in deserialize_message(data, TFMessage).transforms:
                st = tr.header.stamp.sec + tr.header.stamp.nanosec * 1e-9 - G
                if tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link':
                    ob.append((st, tr.transform.translation.x, tr.transform.translation.y, yaw_of(tr.transform.rotation)))
                elif tr.header.frame_id == 'map' and tr.child_frame_id == 'odom':
                    mo.append((st, tr.transform.translation.x, tr.transform.translation.y, yaw_of(tr.transform.rotation)))
        elif topic in ('/local_costmap/costmap', '/global_costmap/costmap') and -3 < t < 3:
            cms.append((t, topic.split('/')[1], deserialize_message(data, OccupancyGrid)))
        elif topic == '/scan' and -1.0 < t < 1.2:
            scans.append((t, deserialize_message(data, LaserScan)))
    ob.sort(); mo.sort(); obt = [o[0] for o in ob]; mot = [m[0] for m in mo]
    print('==== %s: 코스트맵 %d 장, 스캔 %d 장' % (name, len(cms), len(scans)))
    for t, which, m in cms:
        st = m.header.stamp.sec + m.header.stamp.nanosec * 1e-9 - G
        i = min(max(bisect.bisect_left(obt, st), 0), len(ob) - 1); _, px, py, pth = ob[i]
        if which == 'global_costmap':   # map 프레임 → 로버 map 자세
            j = min(max(bisect.bisect_left(mot, st), 0), len(mo) - 1); _, ax, ay, ath = mo[j]
            px, py, pth = ax + px * math.cos(ath) - py * math.sin(ath), ay + px * math.sin(ath) + py * math.cos(ath), ath + pth
        d = np.array(m.data, dtype=np.int16).reshape(m.info.height, m.info.width); jj, ii = np.where(d >= 99)
        X = m.info.origin.position.x + (ii + 0.5) * m.info.resolution; Y = m.info.origin.position.y + (jj + 0.5) * m.info.resolution
        c, s = math.cos(-pth), math.sin(-pth); rx = (X - px) * c - (Y - py) * s; ry = (X - px) * s + (Y - py) * c
        dist = np.hypot(np.maximum(np.abs(rx) - HL, 0), np.maximum(np.abs(ry) - HW, 0))
        sel = dist < 0.30
        cells = sorted(zip(dist[sel], rx[sel], ry[sel], d[jj[sel], ii[sel]]))[:6]
        print('  t %+5.2f %-6s 차체 0.30 m 안 99/100 셀 %2d 개: %s' % (t, which.split('_')[0], sel.sum(), ' '.join('(%+.2f,%+.2f)%d@%.2f' % (cx, cy, v, dd) for dd, cx, cy, v in cells)))
    for t, sc in scans[::3]:
        rr = np.asarray(sc.ranges, dtype=np.float64); aa = sc.angle_min + np.arange(rr.size) * sc.angle_increment
        ok = np.isfinite(rr) & (rr > sc.range_min) & (rr < 0.8)
        bx = LX + rr[ok] * np.cos(aa[ok] + LYAW); by = rr[ok] * np.sin(aa[ok] + LYAW)
        dd = np.hypot(np.maximum(np.abs(bx) - HL, 0), np.maximum(np.abs(by) - HW, 0))
        near = dd < 0.30
        pts = sorted(zip(dd[near], bx[near], by[near]))[:6]
        print('  t %+5.2f scan   차체 0.30 m 안 점 %3d 개 (range_min %.2f): %s' % (t, near.sum(), sc.range_min, ' '.join('(%+.2f,%+.2f)@%.2f' % (x, y, q) for q, x, y in pts)))
