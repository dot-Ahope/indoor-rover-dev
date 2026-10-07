#!/usr/bin/env python3
"""10-07 §5: f2c2 W3 떨림(러너 t 188~236) — TF·토픽 stamp 지연(bag 수신 시각 − header stamp)과 stamp 간격을 6 s 창별로.
   대상: TF map→odom, TF odom→base_link, /odometry/filtered, /scan, /local_costmap/costmap, /cmd_vel 수신 간격. 인자: BAG T0(러너 시작 epoch) OUT"""
import sys, numpy as np, rosbag2_py
from rclpy.serialization import deserialize_message
from rosidl_runtime_py.utilities import get_message
BAG, T0, OUT = sys.argv[1], float(sys.argv[2]), sys.argv[3]
r = rosbag2_py.SequentialReader(); r.open(rosbag2_py.StorageOptions(uri=BAG, storage_id='sqlite3'), rosbag2_py.ConverterOptions('cdr', 'cdr'))
types = {t.name: t.type for t in r.get_all_topics_and_types()}
st = lambda h: h.stamp.sec + h.stamp.nanosec * 1e-9
D = {k: [] for k in ('mo', 'ob', 'odom', 'scan', 'lcm', 'cmd')}
while r.has_next():
    tp, data, ts = r.read_next(); t = ts * 1e-9
    if tp == '/tf':
        for x in deserialize_message(data, get_message(types[tp])).transforms:
            k = (x.header.frame_id, x.child_frame_id)
            if k == ('map', 'odom'): D['mo'].append((t, st(x.header)))
            elif k == ('odom', 'base_link'): D['ob'].append((t, st(x.header)))
    elif tp in ('/odometry/filtered', '/scan', '/local_costmap/costmap'):
        D[{'/odometry/filtered': 'odom', '/scan': 'scan', '/local_costmap/costmap': 'lcm'}[tp]].append((t, st(deserialize_message(data, get_message(types[tp])).header)))
    elif tp == '/cmd_vel': D['cmd'].append((t, t))
np.savez(OUT, **{k: np.array(v) for k, v in D.items()})
print('창(러너 s) | 지연 = 수신 − stamp 중앙/최대 (s): map→odom | odom→base | /odometry | /scan | 로컬 코스트맵 || stamp 간격 최대: map→odom | odom→base | cmd_vel 수신 간격 최대')
for a in range(150, 330, 6):
    row = []
    for k in ('mo', 'ob', 'odom', 'scan', 'lcm'):
        X = np.array(D[k]); s = (X[:, 0] - T0 >= a) & (X[:, 0] - T0 < a + 6); lag = X[s, 0] - X[s, 1]
        row.append('%.2f/%.2f' % (np.median(lag), lag.max()) if s.any() else '-')
    gaps = []
    for k in ('mo', 'ob', 'cmd'):
        X = np.array(D[k]); s = (X[:, 0] - T0 >= a) & (X[:, 0] - T0 < a + 6); u = np.unique(X[s, 1]); gaps.append('%.2f' % np.diff(u).max() if len(u) > 1 else '-')
    print('%3d~%3d | %s || %s' % (a, a + 6, ' | '.join(row), ' | '.join(gaps)))
