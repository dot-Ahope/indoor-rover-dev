#!/usr/bin/env python3
"""10-01 §8.16: f2a6 목표 3(C→D) 동안 경로가 왜 바뀌었나.
   ① 모든 /plan 을 y −3.0~−4.5 구간(책상 줄)을 지나는 x 로 분류: 서(x<−1)·가운데(0.5~1.4)·동(x>2.5), 시각·경로 길이
   ② /global_costmap/costmap 을 10 s 마다 저장(npz) — 세 통로 띠의 최대 비용·치명(≥253) 셀 수
   ③ 로버 map 위치(0.5 s)
   출력: 표 + /tmp/f2a6_gcm.npz(코스트맵 스냅샷·경로·궤적)"""
import sys, math, numpy as np, rosbag2_py
from rclpy.serialization import deserialize_message
from rosidl_runtime_py.utilities import get_message
r = rosbag2_py.SequentialReader(); r.open(rosbag2_py.StorageOptions(uri=sys.argv[1], storage_id='sqlite3'), rosbag2_py.ConverterOptions('cdr', 'cdr'))
types = {t.name: t.type for t in r.get_all_topics_and_types()}
T3 = float(sys.argv[2])   # 목표 3 시작 epoch
plans, snaps, last_snap = [], [], 0
BANDS = {'서': (-2.1, -0.9), '가운데': (0.6, 1.3), '동': (2.6, 3.6)}; Y0, Y1 = -4.5, -3.0
while r.has_next():
    tp, data, ts = r.read_next(); t = ts * 1e-9
    if t < T3 - 2: continue
    if tp == '/plan':
        m = deserialize_message(data, get_message(types[tp])); xy = np.array([[p.pose.position.x, p.pose.position.y] for p in m.poses])
        if len(xy) < 2: continue
        band = xy[(xy[:, 1] < Y1) & (xy[:, 1] > Y0)]
        cls = '?' if not len(band) else ('서' if band[:, 0].mean() < -0.9 else '가운데' if band[:, 0].mean() < 1.6 else '동')
        plans.append((t - T3, cls, np.hypot(*np.diff(xy, axis=0).T).sum(), xy[::4]))
    elif tp == '/global_costmap/costmap' and t - last_snap >= 10:
        m = deserialize_message(data, get_message(types[tp])); last_snap = t
        g = np.array(m.data, dtype=np.int16).reshape(m.info.height, m.info.width)
        snaps.append((t - T3, m.info.origin.position.x, m.info.origin.position.y, m.info.resolution, g))
print('경로 %d 개' % len(plans))
prev = None
for t, c, L, _ in plans:
    if c != prev: print('  %6.1f s  → %s 경로 (길이 %.2f m)' % (t, c, L)); prev = c
from collections import Counter; print('  분류 개수:', dict(Counter(p[1] for p in plans)))
print('코스트맵 스냅샷(10 s): 시각 | 통로 띠(y %.1f~%.1f)별 치명 셀 수·최대 비용' % (Y0, Y1))
for t, ox, oy, res, g in snaps:
    s = []
    for n, (x0, x1) in BANDS.items():
        c0, c1 = int((x0 - ox) / res), int((x1 - ox) / res); r0, r1 = int((Y0 - oy) / res), int((Y1 - oy) / res)
        sub = g[r0:r1, c0:c1]; s.append('%s 치명 %3d·최대 %3d' % (n, (sub >= 253).sum(), sub.max()))
    print('  %6.1f s | %s' % (t, ' | '.join(s)))
np.savez_compressed('/tmp/f2a6_gcm.npz', snaps_t=np.array([s[0] for s in snaps]), snaps_g=np.array([s[4] for s in snaps]),
                    origin=np.array([snaps[0][1], snaps[0][2], snaps[0][3]]), plans_t=np.array([p[0] for p in plans]),
                    plans_c=np.array([p[1] for p in plans]), plans_xy=np.array([p[3] for p in plans], dtype=object), allow_pickle=True)
