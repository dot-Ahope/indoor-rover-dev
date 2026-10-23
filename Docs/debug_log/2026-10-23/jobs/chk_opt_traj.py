#!/usr/bin/env python3
"""chk_opt_traj — MPPI 최적 궤적(32 점, 0.1 s 간격)의 점간 이동 거리 = 단계별 속도를 시각별로(2026-10-23 §7, PC).
  왜: 정지 중 최적 궤적은 3.2 s 에 0.21 m 앞으로 가는데 명령은 0 — 앞쪽 단계가 0 이고 뒤쪽만 움직이는 '나중에 출발' 해인지 확인.
  인자: bag 시각들(s, 쉼표)"""
import sys
from pathlib import Path
import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
bag = sys.argv[1]; TQ = [float(v) for v in sys.argv[2].split(',')]; got = {}
with AnyReader([Path(bag)], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
    T0 = rd.start_time * 1e-9
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic == '/trajectories']):
        tt = t * 1e-9 - T0
        for q in TQ:
            if q not in got and tt >= q:
                m = rd.deserialize(raw, c.msgtype); P = np.array([[mk.pose.position.x, mk.pose.position.y] for mk in sorted([mk for mk in m.markers if mk.ns == 'Optimal Trajectory'], key=lambda z: z.id)])
                got[q] = (tt, np.linalg.norm(np.diff(P, axis=0), axis=1) / 0.1)
for q in TQ:
    if q in got:
        tt, v = got[q]; print('t %6.2f · 단계 속도(m/s) 앞 8: %s · 9~16: %s · 17~31: %s' % (tt, ' '.join('%.3f' % x for x in v[:8]), ' '.join('%.3f' % x for x in v[8:16]), ' '.join('%.3f' % x for x in v[16:])))
