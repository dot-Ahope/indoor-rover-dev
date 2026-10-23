#!/usr/bin/env python3
"""anal_plan_series — 복귀 중 다시 그려진 전역 경로(/plan · /plan_smoothed)마다 실제 상자까지의 여유를, 출발점(로버 자리) 근처를 빼고 (2026-10-23 §4, PC).
  왜: §2~§3 — PathAlign 은 꺼지지 않았고 로버는 최신 경로를 ±4 cm 로 따라감. 그렇다면 다시 그려진 경로 자체가 상자에 붙었나?
      §1 의 계획기 흉내(Dijkstra)는 t 203 에 12 cm 인데 기록 /plan 은 4.3 cm — NavFn(퍼텐셜 기울기 따라 그림)이 흉내보다 붙는지.
  출력: 경로마다 시각 · 출발 자리 · 출발에서 0.3 m 넘게 떨어진 경로점만으로 잰 실제 상자 여유(− 반폭 0.165) · 그 점 위치, 같은 시각 흉내 k 2.0 값은 §1 표 참고.
  인자: bag 시작s 끝s"""
import sys, math
from pathlib import Path
import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
bag, TA, TB = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
BOX = (1.151, 1.261, -0.20, -0.02); BOXP = np.array([[x, y] for x in np.linspace(BOX[0], BOX[1], 12) for y in np.linspace(BOX[2], BOX[3], 19)])
with AnyReader([Path(bag)], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
    T0 = rd.start_time * 1e-9; rows = []
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/plan', '/plan_smoothed')]):
        tt = t * 1e-9 - T0
        if not (TA <= tt <= TB): continue
        m = rd.deserialize(raw, c.msgtype); P = np.array([[p.pose.position.x, p.pose.position.y] for p in m.poses])
        if len(P) < 3: continue
        far = np.linalg.norm(P - P[0], axis=1) > 0.30; Q = P[far]
        if not len(Q): continue
        d = np.min(np.hypot(Q[:, None, 0] - BOXP[None, :, 0], Q[:, None, 1] - BOXP[None, :, 1]), axis=1); k = int(np.argmin(d))
        rows.append((tt, c.topic, P[0], float(d[k]) - 0.165, Q[k], m.header.frame_id))
print('bag %s · t %.0f~%.0f s · 여유 = 출발에서 0.30 m 넘는 경로점 ↔ 실제 상자 − 0.165' % (Path(bag).name, TA, TB))
for tt, tp, s, cl, q, fr in rows:
    print(' %6.1f %-15s 출발 (%5.2f, %5.2f) · 여유 %+5.1f cm @ (%.2f, %.2f) [%s]' % (tt, tp, s[0], s[1], 100 * cl, q[0], q[1], fr))
