#!/usr/bin/env python3
"""anal_mppi_stop — MPPI 가 스스로 0 근처를 고른 구간에서 무엇과 무엇이 맞섰나(2026-10-23 §7, PC, 로버 안 움직임).
  왜: 사용자 — f2pa2 5.5 s 정지(사건 없음)가 경로 정렬 가중 28 탓인지 bag 으로 확인. 정지 중 명령은 계속 나오며 0 근처(§6.2).
  시각마다(odom 기준):
    - 로버 자세 · 명령 v ω
    - 최적 궤적(/trajectories 'Optimal Trajectory' 32 점 = 3.2 s): 총 길이, 끝점의 앞(+)/뒤 · 옆 변위, 끝 방향 변화
    - 컨트롤러 경로(/transformed_global_plan): 로버에서 경로 가장 가까운 점까지 옆 거리, 경로 0.3 m 앞 방향 − 로버 방향
    - 목표(러너의 목표 2, map → odom): 거리 · 방위 − 로버 방향, 목표 방향 − 로버 방향. 크리틱 문턱 — GoalCritic 1.0 m · GoalAngle 0.4 m ·
      PreferForward 0.4 m(목표 0.4 m 안에선 꺼짐) · 경로 크리틱 0.2 m(목표 0.2 m 안에선 꺼짐).
  인자: bag 시작s 끝s 목표x,y,yaw° [간격 s=0.5]"""
import sys, math, bisect
from pathlib import Path
import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
bag, TA, TB = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]); GX, GY, GYAW = (float(v) for v in sys.argv[4].split(',')); GYAW = math.radians(GYAW)
DT = float(sys.argv[5]) if len(sys.argv) > 5 else 0.5
yq = lambda q: math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
wrap = lambda a: math.atan2(math.sin(a), math.cos(a))
MO, OB, TR, TP, CMD = [], [], [], [], []
with AnyReader([Path(bag)], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
    T0 = rd.start_time * 1e-9
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/tf', '/trajectories', '/transformed_global_plan', '/cmd_vel')]):
        tt = t * 1e-9 - T0
        if c.topic != '/tf' and not (TA - 1 <= tt <= TB + 1): continue
        m = rd.deserialize(raw, c.msgtype)
        if c.topic == '/tf':
            for tr in m.transforms:
                v = (tr.transform.translation.x, tr.transform.translation.y, yq(tr.transform.rotation))
                if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom': MO.append((tt, v))
                elif tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link': OB.append((tt, v))
        elif c.topic == '/trajectories':
            P = np.array([[mk.pose.position.x, mk.pose.position.y] for mk in sorted([mk for mk in m.markers if mk.ns == 'Optimal Trajectory'], key=lambda q: q.id)])
            TR.append((tt, P))
        elif c.topic == '/transformed_global_plan': TP.append((tt, np.array([[p.pose.position.x, p.pose.position.y] for p in m.poses]) if m.poses else np.zeros((0, 2))))
        else: CMD.append((tt, m.linear.x, m.angular.z))
for L in (MO, OB): L.sort(key=lambda q: q[0])
ts = lambda L: [q[0] for q in L]; MOt, OBt, TRt, TPt, CMt = ts(MO), ts(OB), ts(TR), ts(TP), ts(CMD)
last = lambda L, Lt, t: L[max(bisect.bisect_right(Lt, t) - 1, 0)]
print('bag %s · t %.0f~%.0f s · 목표 map (%.2f, %.2f, %.0f°) · 각도는 모두 로버 방향 기준(+ = 왼쪽)' % (Path(bag).name, TA, TB, GX, GY, math.degrees(GYAW)))
print('   t   | v · ω         | 최적 궤적 길이 · 끝 앞/옆 · 끝 방향 | 경로 옆거리 · 경로 방향 | 목표 거리 · 방위 · 목표 방향')
t = TA
while t <= TB + 1e-9:
    p = last(OB, OBt, t)[1]; mo = last(MO, MOt, t)[1]
    c, s = math.cos(-mo[2]), math.sin(-mo[2]); dx, dy = GX - mo[0], GY - mo[1]; g = (c * dx - s * dy, s * dx + c * dy); gyaw = GYAW - mo[2]   # 목표 → odom
    cv = last(CMD, CMt, t); P = last(TR, TRt, t)[1]; Q = last(TP, TPt, t)[1]
    ch, sh = math.cos(-p[2]), math.sin(-p[2]); loc = lambda xy: ((xy[0] - p[0]) * ch - (xy[1] - p[1]) * sh, (xy[0] - p[0]) * sh + (xy[1] - p[1]) * ch)
    if len(P) > 1:
        L = float(np.sum(np.linalg.norm(np.diff(P, axis=0), axis=1))); e = loc(P[-1]); d2 = P[-1] - P[-2]; eh = math.degrees(wrap(math.atan2(d2[1], d2[0]) - p[2])) if np.linalg.norm(d2) > 1e-4 else float('nan')
        trs = '%.3f m · %+.3f/%+.3f · %+4.0f°' % (L, e[0], e[1], eh)
    else: trs = '—'
    if len(Q) > 2:
        i = int(np.argmin(np.linalg.norm(Q - np.array(p[:2]), axis=1))); off = loc(Q[i])[1]
        sacc = np.r_[0, np.cumsum(np.linalg.norm(np.diff(Q[i:], axis=0), axis=1))]; j = i + int(np.searchsorted(sacc, 0.3)); j = min(j, len(Q) - 1)
        ph = math.degrees(wrap(math.atan2(Q[j][1] - Q[i][1], Q[j][0] - Q[i][0]) - p[2])) if j > i else float('nan')
        pls = '%+.3f m · %+4.0f°' % (off, ph)
    else: pls = '—'
    gd = math.hypot(g[0] - p[0], g[1] - p[1]); gb = math.degrees(wrap(math.atan2(g[1] - p[1], g[0] - p[0]) - p[2])); ga = math.degrees(wrap(gyaw - p[2]))
    print(' %6.1f | %+.3f %+.2f | %s | %s | %.2f m · %+4.0f° · %+4.0f°%s' % (t, cv[1], cv[2], trs, pls, gd, gb, ga, ' (GoalCritic 켜짐)' if gd < 1.0 else ''))
    t += DT
