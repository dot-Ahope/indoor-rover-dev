#!/usr/bin/env python3
"""anal_leg_env — 한 구간 동안 0.5 s 마다: 지령 v · 직전 1 s /cmd_vel 수(컨트롤러 주기) · 차체(0.52 × 0.35 직사각형)와
  로컬 코스트맵 치명(≥ 99) 칸까지 거리와 그 칸의 차체 기준 방향(앞/옆) · 차체와 라이다 점 최소 거리 (2026-10-28 §12, PC).
  로컬 코스트맵 · 라이다는 odom 에서 봄(odom→base_link). 인자: bag폴더 시작epoch 길이s 이름"""
import sys, math
import numpy as np
from pathlib import Path
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
HL, HW = 0.26, 0.175
bag, t0, dur, name = Path(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3]), sys.argv[4]; t1 = t0 + dur
yaw = lambda q: math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
ob, cv, LC, SC, static = [], [], [], [], {}
def T3(tr):
    a = yaw(tr.rotation); c, s = math.cos(a), math.sin(a); return np.array([[c, -s, tr.translation.x], [s, c, tr.translation.y], [0, 0, 1]])
with AnyReader([bag], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/tf', '/tf_static', '/cmd_vel', '/local_costmap/costmap', '/scan')]):
        ts = t * 1e-9
        if c.topic != '/tf_static' and not t0 - 2 <= ts <= t1: continue
        m = rd.deserialize(raw, c.msgtype)
        if c.topic == '/tf_static':
            for tr in m.transforms: static[tr.child_frame_id] = (tr.header.frame_id, T3(tr.transform))
        elif c.topic == '/tf':
            for tr in m.transforms:
                if tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link': ob.append((ts, T3(tr.transform)))
        elif c.topic == '/cmd_vel': cv.append((ts, m.linear.x, m.angular.z))
        elif c.topic == '/local_costmap/costmap':
            i = m.info; g = np.array(m.data, np.int16).reshape(i.height, i.width); J, I = np.nonzero(g >= 99)
            LC.append((ts, np.c_[i.origin.position.x + (I + .5) * i.resolution, i.origin.position.y + (J + .5) * i.resolution]))
        else:
            a = m.angle_min + m.angle_increment * np.arange(len(m.ranges)); r = np.array(m.ranges, np.float32); ok = np.isfinite(r) & (r > m.range_min) & (r < m.range_max)
            SC.append((ts, m.header.frame_id, np.c_[r[ok] * np.cos(a[ok]), r[ok] * np.sin(a[ok]), np.ones(ok.sum())]))
last = lambda L, t: L[max(np.searchsorted([x[0] for x in L], t, side='right') - 1, 0)]
def chain(f):
    M = np.eye(3)
    while f != 'base_link': p, mm = static[f]; M = mm @ M; f = p
    return M
def rect(P):   # P: base_link 좌표 점들 → 차체 바깥까지 거리 · 가장 가까운 점 방향(도, 0 = 앞)
    if not len(P): return 9.9, 0.0
    d = np.hypot(np.maximum(np.abs(P[:, 0]) - HL, 0), np.maximum(np.abs(P[:, 1]) - HW, 0)); k = int(np.argmin(d))
    return float(d[k]), math.degrees(math.atan2(P[k, 1], P[k, 0]))
print('== %s  (t 0 = epoch %.2f)' % (name, t0))
print('   t s | v | cmd 수/1 s | 로컬 치명 ↔ 차체 m @ 방향 | 라이다 ↔ 차체 m @ 방향')
for t in np.arange(t0, t1, 0.5):
    Mi = np.linalg.inv(last(ob, t)[1]); k = last(cv, t); v = k[1] if t - k[0] < 0.6 else 0.0
    n = sum(1 for x in cv if t - 1 < x[0] <= t)
    _, P = last(LC, t); P = (Mi @ np.c_[P, np.ones(len(P))].T).T[:, :2] if len(P) else P
    dl, al = rect(P)
    z = last(SC, t); L = (chain(z[1]) @ z[2].T).T[:, :2]; ds, as_ = rect(L)
    print('   %5.1f | %+.3f | %2d | %.3f @ %+4.0f° | %.3f @ %+4.0f°' % (t - t0, v, n, dl, al, ds, as_))
