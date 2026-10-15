#!/usr/bin/env python3
"""anal_memory_shift — odom 에 기억된 칸이 '처음 찍힌 순간'과 '나중 순간' 사이 map→odom 변화 때문에 지도(실제 세계) 위에서 얼마나 밀렸는지. (2026-10-15 §24, 오늘만)
  왜: 정지 관측(P1 · P2 · 정면)은 0~3 cm 로 정확했는데 실패 때는 6~7 cm 과장 → 움직이며 찍혀 odom 에 남은 칸이 map→odom 보정 변화만큼 밀렸는지.
  방법: 칸의 지도 좌표(나중 순간 기준)를 나중 순간 map→odom 으로 odom 좌표로 바꾼 뒤(칸은 odom 에 고정), 처음 순간 map→odom 으로 다시 지도로 → 두 지도 좌표 차 = 기억 밀림.
        (처음 순간엔 그 칸이 실제 물체 자리에 찍혔다고 가정 — 그때의 map 이 실제와 맞다는 가정)
  인자: bag 처음HH:MM:SS.f 나중HH:MM:SS.f '칸x,칸y;...'(나중 순간 지도 좌표)"""
import sys, time, math
from pathlib import Path
import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
yq = lambda q: math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
bag, ha, hb, cells = sys.argv[1:5]; C = [tuple(float(v) for v in s.split(',')) for s in cells.split(';')]
def at(h): hms, _, fr = h.partition('.'); return hms, (float('0.' + fr) if fr else 0)
mo = []
with AnyReader([Path(bag)], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic == '/tf']):
        for tr in rd.deserialize(raw, c.msgtype).transforms:
            if tr.child_frame_id == 'odom' and tr.header.frame_id == 'map': mo.append((t / 1e9, tr.transform.translation.x, tr.transform.translation.y, yq(tr.transform.rotation)))
mo = np.array(mo); day = time.strftime('%Y-%m-%d ', time.localtime(mo[0, 0]))
T = lambda h: time.mktime(time.strptime(day + at(h)[0], '%Y-%m-%d %H:%M:%S')) + at(h)[1]
pick = lambda t: mo[max(0, np.searchsorted(mo[:, 0], t) - 1)]
A = pick(T(ha)); B = pick(T(hb))
print('map→odom 처음 %s (%.3f, %.3f, %+.2f°) · 나중 %s (%.3f, %.3f, %+.2f°)' % (ha, A[1], A[2], math.degrees(A[3]), hb, B[1], B[2], math.degrees(B[3])))
for x, y in C:
    c, s = math.cos(B[3]), math.sin(B[3]); dx, dy = x - B[1], y - B[2]; ox = c * dx + s * dy; oy = -s * dx + c * dy   # 나중 지도 → odom
    c2, s2 = math.cos(A[3]), math.sin(A[3]); ax_ = A[1] + c2 * ox - s2 * oy; ay_ = A[2] + s2 * ox + c2 * oy          # odom → 처음 지도
    print('  칸 나중 지도 (%.3f, %.3f) ← 처음 찍힐 때 지도 (%.3f, %.3f) · 밀림 Δx %+.1f cm · Δy %+.1f cm · 크기 %.1f cm' % (x, y, ax_, ay_, 100 * (x - ax_), 100 * (y - ay_), 100 * math.hypot(x - ax_, y - ay_)))
