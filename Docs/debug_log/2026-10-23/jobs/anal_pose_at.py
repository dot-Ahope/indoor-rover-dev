#!/usr/bin/env python3
"""anal_pose_at — 지정 시각(현지 HH:MM:SS.ss)들의 로버 지도 자세(map→odom ∘ odom→base_link) 출력(10-23 §20.3, PC). 인자: bag 시각...
  bag 시작 시각을 로컬 시간으로 바꿔 맞춤(time.localtime)."""
import sys, math, bisect, time
from pathlib import Path
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
yq = lambda q: math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
def comp(a, b):
    c, s = math.cos(a[2]), math.sin(a[2]); return (a[0] + c * b[0] - s * b[1], a[1] + s * b[0] + c * b[1], a[2] + b[2])
MO, OB = [], []
with AnyReader([Path(sys.argv[1])], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic == '/tf']):
        for tr in rd.deserialize(raw, c.msgtype).transforms:
            v = (tr.transform.translation.x, tr.transform.translation.y, yq(tr.transform.rotation))
            if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom': MO.append((t * 1e-9, v))
            elif tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link': OB.append((t * 1e-9, v))
for L in (MO, OB): L.sort(key=lambda q: q[0])
at = lambda L, t: L[max(bisect.bisect_right([q[0] for q in L], t) - 1, 0)][1]
lt = time.localtime(OB[0][0]); day0 = OB[0][0] - (lt.tm_hour * 3600 + lt.tm_min * 60 + lt.tm_sec + OB[0][0] % 1)
for s in sys.argv[2:]:
    h, m, sec = s.split(':'); t = day0 + int(h) * 3600 + int(m) * 60 + float(sec)
    p = comp(at(MO, t), at(OB, t)); print('%s  (%.2f, %.2f)  yaw %.0f°' % (s, p[0], p[1], math.degrees(p[2])))
