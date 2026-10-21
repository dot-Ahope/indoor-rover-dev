#!/usr/bin/env python3
"""anal_cmd_dips — 주행 중 /cmd_vel 전진 명령이 0 근처(< 0.01 m/s)로 떨어진 '짧은 멈칫'을 묶어 세고, 바로 앞(≤ 1.5 s) nav2 사건과 맞춘다. (2026-10-21 §11, PC)
  인자: bag nav2사건파일('HH:MM:SS 메시지' 줄)   — 시각 해상도가 1 s 라 맞춤은 대략."""
import sys, datetime
from pathlib import Path
import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
bag, evf = sys.argv[1:3]; CV = []
with AnyReader([Path(bag)], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic == '/cmd_vel']):
        m = rd.deserialize(raw, c.msgtype); CV.append((t * 1e-9, m.linear.x, m.angular.z))
CV = np.array(CV); mv = np.nonzero(np.abs(CV[:, 1]) > 0.02)[0]; a, b = mv[0], mv[-1]   # 처음 ~ 마지막 전진 명령
d0 = datetime.datetime.fromtimestamp(CV[0, 0]).date()
EV = []
for l in open(evf, encoding='utf-8', errors='replace'):
    p = l.strip().split(' ', 1)
    if len(p) == 2 and p[0].count(':') == 2:
        EV.append((datetime.datetime.combine(d0, datetime.datetime.strptime(p[0], '%H:%M:%S').time()).timestamp(), p[1]))
low = np.abs(CV[a:b, 1]) < 0.01; idx = np.nonzero(low)[0] + a; groups = []
for i in idx:
    if groups and CV[i, 0] - CV[groups[-1][-1], 0] < 0.5: groups[-1].append(i)
    else: groups.append([i])
kinds = {}
print('전진 명령 구간 %.1f s · 0 근처로 떨어진 묶음 %d 번' % (CV[b, 0] - CV[a, 0], len(groups)))
for g in groups:
    t1, t2 = CV[g[0], 0], CV[g[-1], 0]; prev = CV[g[0] - 1, 0]
    near = [m for t, m in EV if t1 - 1.5 <= t <= t1 + 1.0]
    k = '사건 없음' if not near else ('컨트롤러 중단/실패' if any('Aborting' in m or 'fail' in m for m in near) else ('새 경로 전달' if any('Passing new path' in m for m in near) else near[0][:30]))
    kinds[k] = kinds.get(k, 0) + 1
    print('  %s t=%.1f 길이 %.2f s · 명령 %d 개 · 직전 명령 간격 %.2f s | %s' % (datetime.datetime.fromtimestamp(t1).strftime('%H:%M:%S'), t1 - CV[0, 0], t2 - t1, len(g), t1 - prev, ' / '.join(m[:60] for m in near[:3]) or '-'))
print('분류:', kinds)
