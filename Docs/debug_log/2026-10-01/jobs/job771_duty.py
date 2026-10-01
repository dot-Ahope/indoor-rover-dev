#!/usr/bin/env python3
"""10-01 §8.26: f2a9 28~42 s — 펌웨어 /rover/status 의 좌우 트랙 tgt·v·d(듀티)·pps 와 map→odom 보정 변화(SLAM 이 휠 이동을 되돌린 양)."""
import sys, math, re, numpy as np, rosbag2_py
from rclpy.serialization import deserialize_message
from rosidl_runtime_py.utilities import get_message
r = rosbag2_py.SequentialReader(); r.open(rosbag2_py.StorageOptions(uri=sys.argv[1], storage_id='sqlite3'), rosbag2_py.ConverterOptions('cdr', 'cdr'))
types = {t.name: t.type for t in r.get_all_topics_and_types()}
T0 = None; rows = []; mo = []
while r.has_next():
    tp, data, ts = r.read_next(); t = ts * 1e-9
    if tp == '/cmd_vel' and T0 is None: T0 = t
    if T0 is None: continue
    if tp == '/rover/status':
        m = deserialize_message(data, get_message(types[tp]))
        for s in m.status:
            kv = {v.key: v.value for v in s.values}
            if 'L' in kv: rows.append((t - T0, kv.get('L'), kv.get('R'), s.message[:40]))
    elif tp == '/tf':
        for x in deserialize_message(data, get_message(types[tp])).transforms:
            if x.header.frame_id == 'map' and x.child_frame_id == 'odom': mo.append((t - T0, x.transform.translation.x, x.transform.translation.y))
mo = np.array(mo)
for t, L, R, msg in rows:
    if 27 <= t <= 42: print('%5.1f L[%s] R[%s] %s' % (t, L, R, msg))
print('-- map→odom 보정 변화(> 3 cm):')
for a, b in zip(mo, mo[1:]):
    if 25 <= b[0] <= 45 and math.hypot(b[1] - a[1], b[2] - a[2]) > 0.03: print('  %5.1f s  %.2f m' % (b[0], math.hypot(b[1] - a[1], b[2] - a[2])))
