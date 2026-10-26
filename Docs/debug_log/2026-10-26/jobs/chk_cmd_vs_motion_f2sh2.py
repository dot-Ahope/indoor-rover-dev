#!/usr/bin/env python3
"""chk_cmd_vs_motion_f2sh2 — f2sh2 굽은 곳(13:18:22~38) 명령(/cmd_vel) 대 실제 움직임(EKF /odometry/filtered · /vslam/odom · 자이로 /imu/data 를 base_link 로) (2026-10-26 §10.2, PC).
  왜: 시뮬(이상적 차동구동 + 회전 이득 0.7)은 이탈을 바로잡는데 실제는 키움 → 명령한 회전 · 전진이 실제로 나왔는지. 0.5 s 평균. 인자: bag"""
import sys, math, time, bisect
from pathlib import Path
import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
def R(x, y, z, w):
    return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)], [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)], [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])
C, E, V, G, W = [], [], [], [], []; ST = {}; fid = None
with AnyReader([Path(sys.argv[1])], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/cmd_vel', '/odometry/filtered', '/vslam/odom', '/imu/data', '/tf_static', '/wheel_odom')]):
        m = rd.deserialize(raw, c.msgtype); ts = t * 1e-9
        if c.topic == '/tf_static':
            for tr in m.transforms: q = tr.transform.rotation; ST[tr.child_frame_id] = (tr.header.frame_id, R(q.x, q.y, q.z, q.w))
        elif c.topic == '/cmd_vel': C.append((ts, m.linear.x, m.angular.z))
        elif c.topic == '/odometry/filtered': E.append((ts, m.twist.twist.linear.x, m.twist.twist.linear.y, m.twist.twist.angular.z))
        elif c.topic == '/vslam/odom': V.append((ts, m.twist.twist.linear.x, m.twist.twist.linear.y))
        elif c.topic == '/wheel_odom': W.append((ts, m.twist.twist.linear.x, m.twist.twist.angular.z))
        else: fid = m.header.frame_id; G.append((ts, m.angular_velocity.x, m.angular_velocity.y, m.angular_velocity.z))
M = np.eye(3); f = fid
while f in ST and f != 'base_link': par, Rm = ST[f]; M = Rm @ M; f = par
G = np.array(G); gz = (M @ G[:, 1:4].T).T[:, 2]
C, E, V, W = map(np.array, (C, E, V, W))
d0 = time.strftime('%Y-%m-%d ', time.localtime(C[0, 0])); ep = lambda s: time.mktime(time.strptime(d0 + s, '%Y-%m-%d %H:%M:%S'))
avg = lambda A, col, a, b: float(A[(A[:, 0] >= a) & (A[:, 0] < b), col].mean()) if ((A[:, 0] >= a) & (A[:, 0] < b)).any() else float('nan')
print(' 시각     | 명령 v   ω    | 휠 v   ω     | EKF v  vy   ω   | vslam vx vy | 자이로 ω | ω 실제/명령')
for t in np.arange(ep('13:18:22'), ep('13:18:38'), 0.5):
    cv, cw = avg(C, 1, t, t + .5), avg(C, 2, t, t + .5); g = float(gz[(G[:, 0] >= t) & (G[:, 0] < t + .5)].mean())
    print(' %s | %+.3f %+.3f | %+.3f %+.3f | %+.3f %+.3f %+.3f | %+.3f %+.3f | %+.3f | %s' % (time.strftime('%H:%M:%S', time.localtime(t)) + '.%d' % int(t % 1 * 10), cv, cw,
        avg(W, 1, t, t + .5), avg(W, 2, t, t + .5), avg(E, 1, t, t + .5), avg(E, 2, t, t + .5), avg(E, 3, t, t + .5), avg(V, 1, t, t + .5), avg(V, 2, t, t + .5), g,
        ('%.2f' % (g / cw)) if abs(cw) > 0.02 else '-'))
