#!/usr/bin/env python3
"""10-01 §8.19: f2a7 bag 의 /plan 시각·시작점·끝점·길이·경유(최소 y·최대 y) — 경로가 어디로 향했나"""
import sys, numpy as np, rosbag2_py
from rclpy.serialization import deserialize_message
from rosidl_runtime_py.utilities import get_message
r = rosbag2_py.SequentialReader(); r.open(rosbag2_py.StorageOptions(uri=sys.argv[1], storage_id='sqlite3'), rosbag2_py.ConverterOptions('cdr', 'cdr'))
types = {t.name: t.type for t in r.get_all_topics_and_types()}; t0 = None; prev = None
while r.has_next():
    tp, data, ts = r.read_next(); t = ts * 1e-9
    if t0 is None: t0 = t
    if tp != '/plan': continue
    m = deserialize_message(data, get_message(types[tp])); xy = np.array([[p.pose.position.x, p.pose.position.y] for p in m.poses])
    if not len(xy): print('%6.1f s 빈 경로' % (t - t0)); continue
    key = (round(xy[-1, 0], 1), round(xy[-1, 1], 1), round(len(xy), -1))
    if key != prev: print('%6.1f s  시작 (%.2f, %.2f) → 끝 (%.2f, %.2f), %d 점, 길이 %.2f m, y 범위 %.2f~%.2f' % (t - t0, xy[0, 0], xy[0, 1], xy[-1, 0], xy[-1, 1], len(xy), np.hypot(*np.diff(xy, axis=0).T).sum(), xy[:, 1].min(), xy[:, 1].max()))
    prev = key
