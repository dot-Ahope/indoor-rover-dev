#!/usr/bin/env python3
"""anal_box_shift_angle — 기억된 상자가 밀린 양(10-13 §6.2) 가운데 '각도(yaw) 몫'과 '위치 몫'을 가른다. (2026-10-14, 오늘만 — 사용자 지적: "1 칸 두꺼워지는 이유에 각도 문제도 있다고 본다")
  생각: 상자는 로버가 d(약 1.5 m) 떨어진 곳에서 한 번 관측돼 odom 좌표에 놓인다. 그 뒤 지도 보정(map→odom)이 바뀐 만큼 상자가 지도 위에서 움직여 보인다.
        그 변화를 '관측 때 로버가 있던 자리'에서 보면 ① 그 자리 자체가 옮겨진 양(위치 몫) ② 그 자리를 축으로 돈 각 × 상자까지 거리(각도 몫)로 나뉜다.
  인자: bag 관측HH:MM:SS 정지HH:MM:SS 상자x 상자y(지도 좌표, 정지 때 기준)"""
import sys, time, math
from pathlib import Path
import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
bag, h0, h1, bx, by = sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4]), float(sys.argv[5])
def T2(tr):
    q = tr.rotation; yaw = math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z)); c, s = math.cos(yaw), math.sin(yaw); return np.array([[c, -s, tr.translation.x], [s, c, tr.translation.y], [0, 0, 1]])
ob = []; mo = []
with AnyReader([Path(bag)], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic == '/tf']):
        for tr in rd.deserialize(raw, c.msgtype).transforms:
            if tr.child_frame_id == 'base_link' and tr.header.frame_id == 'odom': ob.append((t / 1e9, T2(tr.transform)))
            elif tr.child_frame_id == 'odom' and tr.header.frame_id == 'map': mo.append((t / 1e9, T2(tr.transform)))
last = lambda L, t: L[max(np.searchsorted([x[0] for x in L], t, side='right') - 1, 0)][1]
day = time.strftime('%Y-%m-%d ', time.localtime(ob[0][0])); ep = lambda s: time.mktime(time.strptime(day + s, '%Y-%m-%d %H:%M:%S')); t0, t1 = ep(h0), ep(h1)
M0, M1 = last(mo, t0), last(mo, t1); box_o = np.linalg.inv(M1) @ np.array([bx, by, 1.0])          # 상자의 odom 좌표(정지 때 지도 위치에서 역산 — odom 에 고정)
rov_o = last(ob, t0)[:, 2]                                                                           # 관측 때 로버의 odom 좌표
box0, box1 = (M0 @ box_o)[:2], (M1 @ box_o)[:2]; rov0, rov1 = (M0 @ rov_o)[:2], (M1 @ rov_o)[:2]
tot = box1 - box0; pos = rov1 - rov0; ang = tot - pos; dth = math.degrees(math.atan2(M1[1, 0], M1[0, 0]) - math.atan2(M0[1, 0], M0[0, 0])); d = np.hypot(*(box0 - rov0))
u = (box0 - rov0) / d; n = np.array([-u[1], u[0]])   # 관측 때 로버→상자 방향과 그 옆 방향
print('%s 관측 %s → 정지 %s | 관측 때 로버↔상자 %.2f m | 보정 각 변화 %+.2f°' % (Path(bag).name, h0, h1, d, dth))
print('  상자가 지도 위에서 움직인 양(전체)  (%+.1f, %+.1f) cm = %.1f cm' % (tot[0] * 100, tot[1] * 100, np.hypot(*tot) * 100))
print('  · 위치 몫(관측 자리 자체의 이동)   (%+.1f, %+.1f) cm = %.1f cm' % (pos[0] * 100, pos[1] * 100, np.hypot(*pos) * 100))
print('  · 각도 몫(각 변화 × %.2f m)        (%+.1f, %+.1f) cm = %.1f cm   [검산: %.2f° × %.2f m = %.1f cm]' % (d, ang[0] * 100, ang[1] * 100, np.hypot(*ang) * 100, abs(dth), d, abs(math.radians(dth)) * d * 100))
print('  시선에 수직인 방향(옆으로 두꺼워 보이는 쪽)으로: 전체 %+.1f cm = 위치 %+.1f + 각도 %+.1f' % (tot @ n * 100, pos @ n * 100, ang @ n * 100))
