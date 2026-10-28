#!/usr/bin/env python3
"""anal_plan_x — 시간 창 안의 /plan 마다 y 값 몇 곳에서 경로의 x(통로 안 가로 위치)와 점 수 · 길이 (2026-10-28 §12, PC).
  인자: bag폴더 시작epoch 끝epoch y1,y2,..."""
import sys, time
import numpy as np
from pathlib import Path
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
bag, t0, t1 = Path(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3]); YS = [float(v) for v in sys.argv[4].split(',')]
with AnyReader([bag], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic == '/plan']):
        ts = t * 1e-9
        if not t0 - 1 <= ts <= t1: continue
        m = rd.deserialize(raw, c.msgtype); P = np.array([[q.pose.position.x, q.pose.position.y] for q in m.poses])
        if not len(P): print('  %+.1f s 빈 경로' % (ts - t0)); continue
        L = np.sum(np.hypot(*np.diff(P, axis=0).T))
        xs = ['y %.1f: x %s' % (y, '%.3f' % P[np.argmin(np.abs(P[:, 1] - y)), 0] if np.min(np.abs(P[:, 1] - y)) < 0.05 else '—') for y in YS]
        print('  %+6.1f s  %3d 점 %.2f m  시작 (%.2f, %.2f) 끝 (%.2f, %.2f) | %s' % (ts - t0, len(P), L, P[0, 0], P[0, 1], P[-1, 0], P[-1, 1], ' · '.join(xs)))
