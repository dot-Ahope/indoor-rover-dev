#!/usr/bin/env python3
"""10-01 §8.37: f2a12 목표 7 — 바퀴 명령(/cmd_vel 류)·경로(/plan) 시계열. 인자: BAG T_START T_END(epoch)"""
import sys, math, numpy as np, rosbag2_py
from rclpy.serialization import deserialize_message
from rosidl_runtime_py.utilities import get_message
BAG, TA, TB = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
r = rosbag2_py.SequentialReader(); r.open(rosbag2_py.StorageOptions(uri=BAG, storage_id='sqlite3'), rosbag2_py.ConverterOptions('cdr', 'cdr'))
types = {t.name: t.type for t in r.get_all_topics_and_types()}
print('토픽:', sorted(k for k in types if 'cmd' in k or 'plan' in k or 'odom' in k))
cmd = {}; plans = []; odo = []
while r.has_next():
    tp, data, ts = r.read_next(); t = ts * 1e-9
    if t > TB: break
    if t < TA: continue
    if 'cmd_vel' in tp:
        m = deserialize_message(data, get_message(types[tp])); m = getattr(m, 'twist', m)
        cmd.setdefault(tp, []).append((t - TA, m.linear.x, m.angular.z))
    elif tp == '/plan':
        m = deserialize_message(data, get_message(types[tp])); p = np.array([[q.pose.position.x, q.pose.position.y] for q in m.poses])
        plans.append((t - TA, p))
    elif tp == '/odometry/filtered':
        m = deserialize_message(data, get_message(types[tp])); odo.append((t - TA, m.twist.twist.linear.x, m.twist.twist.angular.z))
for tp, v in cmd.items():
    v = np.array(v); print('\n==', tp, len(v), '개')
    for a in range(0, int(TB - TA), 3):
        w = v[(v[:, 0] >= a) & (v[:, 0] < a + 3)]
        if len(w): print('  %3d~%3d s vx 평균 %+.3f 최소 %+.3f 최대 %+.3f | wz 평균 %+.3f 최소 %+.3f 최대 %+.3f | vx 부호 바뀜 %d wz 부호 바뀜 %d' % (a, a + 3, w[:, 1].mean(), w[:, 1].min(), w[:, 1].max(), w[:, 2].mean(), w[:, 2].min(), w[:, 2].max(), int((np.diff(np.sign(w[:, 1])) != 0).sum()), int((np.diff(np.sign(w[:, 2])) != 0).sum())))
o = np.array(odo)
if len(o): print('\n== EKF 실제 속도: vx 절대 평균 %.4f wz 절대 평균 %.4f' % (abs(o[:, 1]).mean(), abs(o[:, 2]).mean()))
print('\n== /plan', len(plans), '개')
for t, p in plans: print('  %.1f s 점 %d 시작 (%.2f,%.2f) 끝 (%.2f,%.2f) x 범위 %.2f~%.2f' % (t, len(p), p[0, 0], p[0, 1], p[-1, 0], p[-1, 1], p[:, 0].min(), p[:, 0].max()))
np.savez('/tmp/f2a12_g7.npz', plans=np.array([p for _, p in plans], dtype=object), pt=np.array([t for t, _ in plans]), **{k.strip('/').replace('/', '_'): np.array(v) for k, v in cmd.items()})
