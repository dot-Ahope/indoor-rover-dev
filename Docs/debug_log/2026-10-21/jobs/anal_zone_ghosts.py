#!/usr/bin/env python3
"""anal_zone_ghosts — 지정 영역에서 주행 한 구간 동안 로컬 코스트맵 LETHAL 이 한 번이라도 된 칸(저장 지도 0.10 m 밖 · 그 순간 라이다 점 0.10 m 밖)을 모두 센다. (2026-10-21 §15, PC)
  왜: 사용자 — "nvblox 만 쓸 때(프로젝터 켬)는 상자 너머 · 문 사이 점이 안 나왔는데 지금은 나온다." 주행 시각 한 점이 아니라 구간 전체로 켬/끔 주행을 비교.
  인자: bag t0 t1 영역들 'x0,x1,y0,y1;...'   출력: 영역별 칸 수 · 칸 목록(처음 시각, 지속 장 수)"""
import sys, math, bisect
from pathlib import Path
import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
bag, ta, tb = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]); R = [[float(v) for v in s.split(',')] for s in sys.argv[4].split(';')]
yaw = lambda q: math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
def comp(a, b):
    c, s = math.cos(a[2]), math.sin(a[2]); return (a[0] + c * b[0] - s * b[1], a[1] + s * b[0] + c * b[1], a[2] + b[2])
LC, MP, MO, OB, SC, ST = [], None, [], [], [], {}
with AnyReader([Path(bag)], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
    t0 = rd.start_time * 1e-9
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/local_costmap/costmap', '/map', '/tf', '/tf_static', '/scan')]):
        tt = t * 1e-9 - t0
        if c.topic in ('/local_costmap/costmap', '/scan') and not (ta - 2 <= tt <= tb): continue
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
            elif tt >= ta: LC.append((tt, g.origin.position.x, g.origin.position.y, g.resolution, A))
for L in (MO, OB): L.sort(key=lambda q: q[0])
MOt = [q[0] for q in MO]; OBt = [q[0] for q in OB]; SCt = [q[0] for q in SC]
at = lambda L, Lt, t: L[max(bisect.bisect_right(Lt, t) - 1, 0)][1]
B2L = (0.0, 0.0, 0.0); f = 'lidar_link'; ch = []
while f in ST and f != 'base_link':
    p, a = ST[f]; ch.append(a); f = p
for a in reversed(ch): B2L = comp(B2L, a)
mx, my, mr, MA = MP; mys, mxs = np.nonzero(MA >= 65); MPt = np.c_[mx + (mxs + 0.5) * mr, my + (mys + 0.5) * mr]
cells = [dict() for _ in R]
for tt, ox, oy, r, A in LC:
    ys, xs = np.nonzero(A >= 100); a = at(MO, MOt, tt); c, s = math.cos(a[2]), math.sin(a[2])
    px, py = ox + (xs + 0.5) * r, oy + (ys + 0.5) * r; X, Y = a[0] + c * px - s * py, a[1] + s * px + c * py
    LP = []
    for i in range(max(bisect.bisect_left(SCt, tt - 1.0), 0), bisect.bisect_right(SCt, tt)):
        ts, a0, da, rg = SC[i]; P = comp(comp(at(MO, MOt, ts), at(OB, OBt, ts)), B2L); ok = np.isfinite(rg) & (rg > 0.05); an = a0 + da * np.arange(len(rg))
        LP.append(np.c_[P[0] + rg[ok] * np.cos(P[2] + an[ok]), P[1] + rg[ok] * np.sin(P[2] + an[ok])])
    LP = np.vstack(LP) if LP else np.zeros((0, 2))
    for k, (x0, x1, y0, y1) in enumerate(R):
        sel = np.nonzero((X >= x0) & (X <= x1) & (Y >= y0) & (Y <= y1))[0]
        for i in sel:
            if np.hypot(MPt[:, 0] - X[i], MPt[:, 1] - Y[i]).min() <= 0.10: continue
            if len(LP) and np.hypot(LP[:, 0] - X[i], LP[:, 1] - Y[i]).min() <= 0.10: continue
            key = (round(X[i] / 0.05) * 0.05, round(Y[i] / 0.05) * 0.05); d = cells[k].setdefault(key, [tt, 0]); d[1] += 1
print('bag %s · 구간 t %.0f~%.0f s · 로컬 코스트맵 %d 장' % (Path(bag).name, ta, tb, len(LC)))
for k, (x0, x1, y0, y1) in enumerate(R):
    print('  영역 x %.2f~%.2f y %.2f~%.2f: 근거 없는 LETHAL 칸 %d 개%s' % (x0, x1, y0, y1, len(cells[k]), '' if not cells[k] else ' — ' + ' '.join('(%.2f,%.2f)t%.0f×%d' % (q[0], q[1], v[0], v[1]) for q, v in sorted(cells[k].items(), key=lambda e: e[1][0])[:12])))
