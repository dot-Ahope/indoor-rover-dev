#!/usr/bin/env python3
"""anal_dip_events — /cmd_vel 전진 명령이 0 근처(< 0.01)로 떨어진 묶음마다, 0.01 s 시각 nav2 사건(앞 2 s ~ 뒤 0.5 s)과 명령값 흐름을 나란히. (2026-10-21 §12, PC)
  인자: bag nav_events_ms.txt('HH:MM:SS.cc 노드 메시지' 줄)"""
import sys, datetime
from pathlib import Path
import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
bag, evf = sys.argv[1:3]; CV = []
with AnyReader([Path(bag)], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic == '/cmd_vel']):
        m = rd.deserialize(raw, c.msgtype); CV.append((t * 1e-9, m.linear.x, m.angular.z))
CV = np.array(CV); d0 = datetime.datetime.fromtimestamp(CV[0, 0]).date(); EV = []
for l in open(evf, encoding='utf-8', errors='replace'):
    p = l.replace(chr(0), '').strip().split(' ', 2)
    if len(p) == 3 and p[0].count(':') == 2 and '.' in p[0]:
        h, cc = p[0].split('.'); tt = datetime.datetime.combine(d0, datetime.datetime.strptime(h, '%H:%M:%S').time()).timestamp() + float('0.' + cc)
        if 'Control loop missed' not in p[2] and 'Received a path to smooth' not in p[2]: EV.append((tt, p[1], p[2]))
mv = np.nonzero(np.abs(CV[:, 1]) > 0.02)[0]; a, b = mv[0], mv[-1]
idx = np.nonzero(np.abs(CV[a:b, 1]) < 0.01)[0] + a; G = []
for i in idx:
    if G and CV[i, 0] - CV[G[-1][-1], 0] < 0.5: G[-1].append(i)
    else: G.append([i])
hm = lambda t: datetime.datetime.fromtimestamp(t).strftime('%H:%M:%S.%f')[:11]
for g in G:
    t1 = CV[g[0], 0]; w = CV[max(g[0] - 4, 0):g[-1] + 4]
    print('\n== 멈칫 %s (명령 0 근처 %d 개 · %.2f s) | 앞뒤 명령 v: %s' % (hm(t1), len(g), CV[g[-1], 0] - t1, ' '.join('%.3f' % v for v in w[:, 1])))
    for tt, n, m in EV:
        if t1 - 2.0 <= tt <= t1 + 0.5: print('   %+5.2f s %-22s %s' % (tt - t1, n[:22], m[:110]))
