#!/usr/bin/env python3
"""chk_slice_tf — §15 틀어진 전역 프레임 앞뒤로 nvblox 슬라이스 원본과 TF 를 메시지마다 (2026-10-27, PC).
  슬라이스(odom): header stamp · 원점 · 크기 · 장애(≤0) 칸 수, 장애 칸 집합의 직전 슬라이스 대비 최적 회전(로버 중심, ±30° 1° 간격) · 이동.
  TF: odom→base_link(EKF) 를 0.1 s 간격으로 — yaw · 위치 튐. 인자: bag폴더 시작HH:MM:SS 끝HH:MM:SS"""
import sys, time, math
import numpy as np
from pathlib import Path
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore, get_types_from_msg
ts_ = get_typestore(Stores.ROS2_HUMBLE)
ts_.register(get_types_from_msg('std_msgs/Header header\nfloat32 resolution\nuint32 width\nuint32 height\ngeometry_msgs/Point origin\nfloat32 unknown_value\nfloat32[] data\n', 'nvblox_msgs/msg/DistanceMapSlice'))
bag = Path(sys.argv[1])
t0 = time.mktime(time.strptime('2026-10-27 ' + sys.argv[2], '%Y-%m-%d %H:%M:%S')); t1 = time.mktime(time.strptime('2026-10-27 ' + sys.argv[3], '%Y-%m-%d %H:%M:%S'))
hs = lambda t: time.strftime('%H:%M:%S', time.localtime(t)) + '.%02d' % int((t % 1) * 100)
def yaw(q): return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
S, ob = [], []
with AnyReader([bag], default_typestore=ts_) as rd:
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/nvblox_node/static_map_slice', '/tf')]):
        ts = t * 1e-9
        if ts < t0 or ts > t1: continue
        m = rd.deserialize(raw, c.msgtype)
        if c.topic == '/tf':
            for tr in m.transforms:
                if tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link':
                    ob.append((ts, tr.header.stamp.sec + tr.header.stamp.nanosec * 1e-9, tr.transform.translation.x, tr.transform.translation.y, math.degrees(yaw(tr.transform.rotation))))
            continue
        d = np.array(m.data, np.float32).reshape(m.height, m.width); J, I = np.nonzero((d <= 0) & (d != m.unknown_value))
        S.append((ts, m.header.stamp.sec + m.header.stamp.nanosec * 1e-9, m.origin.x, m.origin.y, m.width, m.height, np.c_[m.origin.x + (I + .5) * m.resolution, m.origin.y + (J + .5) * m.resolution]))
def best_rot(A, B, cx, cy):   # B 를 (cx, cy) 중심으로 돌려 A 와 5 cm 칸 겹침 최대
    ka = set(map(tuple, np.round(A / 0.05).astype(int))); out = (0, 0)
    for deg in range(-30, 31):
        a = math.radians(deg); c, s = math.cos(a), math.sin(a); X = B - [cx, cy]
        R = np.c_[c * X[:, 0] - s * X[:, 1], s * X[:, 0] + c * X[:, 1]] + [cx, cy]
        n = len(ka & set(map(tuple, np.round(R / 0.05).astype(int))))
        if n > out[0]: out = (n, deg)
    return out
print('슬라이스(odom): 수신 · stamp · 원점 · 크기 · 장애 칸 · 직전과 겹침(회전 0) · 최적 회전(로버 중심)')
for k, (ts, st, ox, oy, w, h, P) in enumerate(S):
    r = min(ob, key=lambda x: abs(x[0] - ts))
    if k:
        A = S[k - 1][6]; ka = set(map(tuple, np.round(A / 0.05).astype(int))); n0 = len(ka & set(map(tuple, np.round(P / 0.05).astype(int))))
        nb, deg = best_rot(A, P, r[2], r[3])
        print('%s stamp %s(%+.2f) 원점 (%.2f, %.2f) %dx%d 장애 %d · 겹침 %d · 최적 %+d° (%d)' % (hs(ts), hs(st), ts - st, ox, oy, w, h, len(P), n0, deg, nb))
print('\nodom→base_link(EKF) 0.1 s 간격: 수신 · stamp · x · y · yaw · 직전 대비 yaw 변화')
last = None
for ts, st, x, y, a in ob:
    if last is None or ts - last[0] >= 0.1:
        print('%s stamp %s (%.3f, %.3f, %.2f°)%s' % (hs(ts), hs(st), x, y, a, '' if last is None else ' Δyaw %+.2f° Δxy %.3f' % (((a - last[4] + 180) % 360) - 180, math.hypot(x - last[2], y - last[3]))))
        last = (ts, st, x, y, a)
