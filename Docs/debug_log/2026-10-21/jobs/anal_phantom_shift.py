#!/usr/bin/env python3
"""anal_phantom_shift — 가설 검사: '카메라 층만' LETHAL 칸은 nvblox 가 odom 좌표로 기억한 진짜 벽 · 상자가, 그 뒤 SLAM 의 map→odom 보정이 바뀌면서
  map 좌표에서 옮겨 찍힌 것인가. (2026-10-21 §13, PC)
  방법: 끝 시각 T 의 유령 칸 p 를 '관측 시각 s 의 map 좌표' 로 되돌림 — p' = MO(s) · MO(T)^-1 · p. s 를 바꿔 가며 p' 가 저장 지도 벽(0.10 m 안)에
        떨어지는 비율을 본다. 기억이 옮겨진 것이면 어떤 s 에서 비율이 크게 오른다(s = T 는 정의상 0 %).
  함께: map→odom 의 시간 변화(위치 · 각) — 유령 칸이 생긴 시각과 비교.
  인자: bag [끝 시각 T = -2] [창 x0,x1,y0,y1]"""
import sys, math, bisect
from pathlib import Path
import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
bag = sys.argv[1]; tq = float(sys.argv[2]) if len(sys.argv) > 2 else -2.0
W = [float(v) for v in sys.argv[3].split(',')] if len(sys.argv) > 3 else [-1.5, 3.5, -2.5, 1.5]


def yaw(q): return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))


def M(a):
    c, s = math.cos(a[2]), math.sin(a[2]); return np.array([[c, -s, a[0]], [s, c, a[1]], [0, 0, 1]])


GC, MP, MO, SC, OB, ST = [], None, [], [], [], {}
with AnyReader([Path(bag)], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
    t0 = rd.start_time * 1e-9; T = tq if tq >= 0 else rd.end_time * 1e-9 - t0 + tq
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/global_costmap/costmap', '/map', '/tf', '/tf_static', '/scan')]):
        tt = t * 1e-9 - t0
        if c.topic in ('/global_costmap/costmap', '/scan') and not (T - 3 <= tt <= T + 1.5): continue
        m = rd.deserialize(raw, c.msgtype)
        if c.topic in ('/tf', '/tf_static'):
            for tr in m.transforms:
                a = (tr.transform.translation.x, tr.transform.translation.y, yaw(tr.transform.rotation))
                if c.topic == '/tf_static': ST[tr.child_frame_id] = (tr.header.frame_id, a)
                elif tr.header.frame_id == 'map' and tr.child_frame_id == 'odom': MO.append((tt, a))
                elif tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link': OB.append((tt, a))
        elif c.topic == '/scan': SC.append((tt, m.angle_min, m.angle_increment, np.array(m.ranges)))
        else:
            g = m.info; A = np.array(m.data, dtype=np.int16).reshape(g.height, g.width)
            if c.topic == '/map': MP = (g.origin.position.x, g.origin.position.y, g.resolution, A)
            else: GC.append((tt, g.origin.position.x, g.origin.position.y, g.resolution, A))
MO.sort(key=lambda q: q[0]); MOt = [q[0] for q in MO]
at = lambda L, Lt, t: L[max(bisect.bisect_right(Lt, t) - 1, 0)][1]
OBt = [q[0] for q in OB]
mx, my, mr, MA = MP; mys, mxs = np.nonzero(MA >= 65); MPt = np.c_[mx + (mxs + 0.5) * mr, my + (mys + 0.5) * mr]
k = max(bisect.bisect_right([g[0] for g in GC], T) - 1, 0); tg, ox, oy, r, A = GC[k]
ys, xs = np.nonzero(A >= 100); P = np.c_[ox + (xs + 0.5) * r, oy + (ys + 0.5) * r]
P = P[(P[:, 0] >= W[0]) & (P[:, 0] <= W[1]) & (P[:, 1] >= W[2]) & (P[:, 1] <= W[3])]


def onmap(Q):
    return np.array([np.hypot(MPt[:, 0] - q[0], MPt[:, 1] - q[1]).min() <= 0.10 for q in Q])


# 라이다 근처 칸 제외(지금 실제로 보이는 것)
LP = []
B2L = np.eye(3); f = 'lidar_link'; ch = []
while f in ST and f != 'base_link':
    p, a = ST[f]; ch.append(a); f = p
for a in reversed(ch): B2L = B2L @ M(a)
for ts, a0, da, rg in SC:
    if not (tg - 1.0 <= ts <= tg + 0.1): continue
    Tm = M(at(MO, MOt, ts)) @ M(at(OB, OBt, ts)) @ B2L; ok = np.isfinite(rg) & (rg > 0.05); an = a0 + da * np.arange(len(rg))
    q = np.c_[rg[ok] * np.cos(an[ok]), rg[ok] * np.sin(an[ok]), np.ones(ok.sum())] @ Tm.T; LP.append(q[:, :2])
LP = np.vstack(LP)
lid = np.array([np.hypot(LP[:, 0] - p[0], LP[:, 1] - p[1]).min() <= 0.10 for p in P])
on0 = onmap(P); G = P[~on0 & ~lid]
print('bag %s · 끝 코스트맵 t=%.1f s · 창 안 LETHAL %d · 유령 후보(지도 · 라이다 둘 다 아님) %d 칸' % (Path(bag).name, tg, len(P), len(G)))
MT = M(at(MO, MOt, tg)); a_T = at(MO, MOt, tg)
print('map→odom: 시작 (%.3f, %.3f, %.2f°) → 끝 (%.3f, %.3f, %.2f°)' % (MO[0][1][0], MO[0][1][1], math.degrees(MO[0][1][2]), a_T[0], a_T[1], math.degrees(a_T[2])))
print('\n관측 시각 s 로 되돌렸을 때 유령 후보가 지도 벽(0.10 m 안)에 떨어지는 비율:')
best = (0, None)
for s in list(np.arange(0, tg, 10.0)) + [tg]:
    Ms = M(at(MO, MOt, s)); Q = (np.c_[G, np.ones(len(G))] @ (Ms @ np.linalg.inv(MT)).T)[:, :2]
    fr = onmap(Q).mean(); a = at(MO, MOt, s)
    print('  s=%5.1f s · map→odom (%.3f, %.3f, %+.2f°) · 되돌린 이동량 중앙 %.3f m → 지도 벽 위 %4.1f %%' % (s, a[0], a[1], math.degrees(a[2]), np.median(np.hypot(*(Q - G).T)), 100 * fr))
    if fr > best[0]: best = (fr, s)
# 대조: 같은 수의 칸을 같은 크기만큼 무작위 방향으로 옮겼을 때
rng = np.random.default_rng(0); sh = np.median(np.hypot(*((np.c_[G, np.ones(len(G))] @ (M(at(MO, MOt, best[1] or 0)) @ np.linalg.inv(MT)).T)[:, :2] - G).T))
ctrl = []
for _ in range(20):
    th = rng.uniform(0, 2 * math.pi); ctrl.append(onmap(G + sh * np.array([math.cos(th), math.sin(th)])).mean())
print('\n최고 %.1f %% @ s=%.0f · 대조(같은 크기 %.3f m 를 무작위 방향으로 20 회): 평균 %.1f %% · 최대 %.1f %%' % (100 * best[0], best[1] or 0, sh, 100 * np.mean(ctrl), 100 * np.max(ctrl)))
ts_ = np.array(MOt); dx = np.array([q[1][0] for q in MO]); dy = np.array([q[1][1] for q in MO]); dth = np.degrees([q[1][2] for q in MO])
print('\nmap→odom 변화(10 s 마다):')
for s in np.arange(0, tg, 10.0):
    i = max(bisect.bisect_right(MOt, s) - 1, 0); print('  t=%5.0f (%.3f, %.3f, %+.2f°)' % (s, dx[i], dy[i], dth[i]))
