#!/usr/bin/env python3
"""anal_pathalign_occ — 상자 옆에서 MPPI PathAlignCritic 이 꺼졌을까: 컨트롤러가 받은 경로(/transformed_global_plan)의 점 중
  로컬 코스트맵에서 '못 쓰는 점'(중심 칸이 내접 99 · 치명 100, 미확인 −1 은 따로 셈)의 비율을 시각별로 (2026-10-23 §3, PC, 로버 안 움직임).
  왜: §2 — f2pi1 은 상자 옆에서 경로보다 상자 쪽으로 10~16 cm 질러감. Nav2 Humble MPPI PathAlignCritic 은 경로의 '가장 가까운 점 ~ 지평 끝이 닿은 점'
      구간에서 못 쓰는 점 비율이 max_path_occupancy_ratio(0.05)를 넘고 그 수가 2 개를 넘으면 그 주기에 적용하지 않는다(소스 critics/path_align_critic.cpp —
      동적 물체가 경로를 막을 때 경로에 붙지 않게 하려는 장치). 꺼지면 경로에 붙잡는 힘이 줄어 질러갈 수 있다(추정).
  근사: '지평 끝이 닿은 점' = 로버에서 경로를 따라 vx_max × 지평(0.08 × 3.2 = 0.26 m) 앞 점. 칸 판정은 메시지 값(0~100) 기준.
  인자: bag 시작s 끝s [간격 s=0.5] [지평 m=0.26]"""
import sys, math, bisect
from pathlib import Path
import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
bag, TA, TB = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]); DT = float(sys.argv[4]) if len(sys.argv) > 4 else 0.5; HOR = float(sys.argv[5]) if len(sys.argv) > 5 else 0.26
yq = lambda q: math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
OB, LC, TP = [], [], []
with AnyReader([Path(bag)], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
    T0 = rd.start_time * 1e-9
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/tf', '/local_costmap/costmap', '/transformed_global_plan')]):
        tt = t * 1e-9 - T0
        if c.topic != '/tf' and not (TA - 2 <= tt <= TB + 1): continue
        m = rd.deserialize(raw, c.msgtype)
        if c.topic == '/tf':
            for tr in m.transforms:
                if tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link': OB.append((tt, (tr.transform.translation.x, tr.transform.translation.y)))
        elif c.topic == '/local_costmap/costmap':
            g = m.info; LC.append((tt, m.header.frame_id, g.origin.position.x, g.origin.position.y, g.resolution, np.array(m.data, np.int16).reshape(g.height, g.width)))
        else: TP.append((tt, m.header.frame_id, np.array([[p.pose.position.x, p.pose.position.y] for p in m.poses]) if m.poses else np.zeros((0, 2))))
OB.sort(key=lambda q: q[0]); OBt = [q[0] for q in OB]; LCt = [q[0] for q in LC]; TPt = [q[0] for q in TP]
last = lambda L, Lt, t: L[max(bisect.bisect_right(Lt, t) - 1, 0)]
print('bag %s · t %.0f~%.0f s · 지평 %.2f m · 경로 프레임 %s · 로컬 코스트맵 프레임 %s' % (Path(bag).name, TA, TB, HOR, TP[0][1] if TP else '-', LC[0][1] if LC else '-'))
print('   t   | 구간 점 수 | 내접·치명 점 | 미확인 점 | 비율(내접·치명) | 비율(+미확인) | PathAlign 적용?')
t = TA; offn = 0; n = 0
while t <= TB + 1e-9:
    _, frp, P = last(TP, TPt, t); _, frc, ox, oy, r, A = last(LC, LCt, t); q = np.array(last(OB, OBt, t)[1])
    if len(P) < 3: t += DT; continue
    i0 = int(np.argmin(np.linalg.norm(P - q, axis=1))); s = np.r_[0, np.cumsum(np.linalg.norm(np.diff(P[i0:], axis=0), axis=1))]
    i1 = i0 + int(np.searchsorted(s, HOR)); seg = P[i0:max(i1, i0 + 1)]
    ij = (((seg[:, 1] - oy) / r).astype(int), ((seg[:, 0] - ox) / r).astype(int)); ok = (ij[0] >= 0) & (ij[0] < A.shape[0]) & (ij[1] >= 0) & (ij[1] < A.shape[1])
    v = np.full(len(seg), -2); v[ok] = A[ij[0][ok], ij[1][ok]]
    bad = int(np.sum(v >= 99)); unk = int(np.sum(v == -1)); rng = max(len(seg), 1)
    on = not ((bad / rng > 0.05) and bad > 2); on2 = not (((bad + unk) / rng > 0.05) and bad + unk > 2)
    n += 1; offn += (not on)
    print(' %6.1f | %4d | %3d | %3d | %5.2f | %5.2f | %s%s' % (t, rng, bad, unk, bad / rng, (bad + unk) / rng, '적용' if on else '**꺼짐**', '' if on == on2 else ' (미확인 포함 시 꺼짐)'))
    t += DT
print('합: %d 시각 중 꺼짐 %d' % (n, offn))
