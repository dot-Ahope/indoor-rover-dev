#!/usr/bin/env python3
"""anal_box_detect — 출발점 낮은 상자 감지 시각(2026-10-22 §2, PC).
  t0 = 상자 중심이 로버 1.4 m 안 · 진행 방향 ±40° 에 처음 든 시각(map→odom→base_link 로 로버 자세).
  로컬 코스트맵(odom)을 map 으로 옮겨 상자 영역 LETHAL(100) 칸 수를 시간순으로 → t0 뒤 처음 ≥ 8 칸이 된 시각과 지연.
  인자: bag [상자 중심 x,y] [영역 x0,x1,y0,y1]"""
import sys, math, bisect
from pathlib import Path
import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore

bag = sys.argv[1]
BX, BY = (float(v) for v in (sys.argv[2] if len(sys.argv) > 2 else '1.25,-0.075').split(','))
X0, X1, Y0, Y1 = (float(v) for v in (sys.argv[3] if len(sys.argv) > 3 else '1.15,1.35,-0.20,0.05').split(','))
RMAX, FOV, NEED = 1.4, math.radians(40), 8
yaw = lambda q: math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))


def comp(a, b):
    c, s = math.cos(a[2]), math.sin(a[2]); return (a[0] + c * b[0] - s * b[1], a[1] + s * b[0] + c * b[1], a[2] + b[2])


MO, OB, LC = [], [], []
with AnyReader([Path(bag)], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
    t0b = rd.start_time * 1e-9
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/tf', '/local_costmap/costmap')]):
        tt = t * 1e-9 - t0b; m = rd.deserialize(raw, c.msgtype)
        if c.topic == '/tf':
            for tr in m.transforms:
                a = (tr.transform.translation.x, tr.transform.translation.y, yaw(tr.transform.rotation))
                if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom': MO.append((tt, a))
                elif tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link': OB.append((tt, a))
        else:
            g = m.info; LC.append((tt, g.origin.position.x, g.origin.position.y, g.resolution, np.array(m.data, dtype=np.int16).reshape(g.height, g.width)))
for L in (MO, OB): L.sort(key=lambda q: q[0])
MOt = [q[0] for q in MO]; OBt = [q[0] for q in OB]
at = lambda L, Lt, t: L[max(bisect.bisect_right(Lt, t) - 1, 0)][1]
# 로버 자세 → t0
t_in = None
for tt, ob in OB:
    if tt < MOt[0]: continue
    p = comp(at(MO, MOt, tt), ob); d = math.hypot(BX - p[0], BY - p[1])
    b = math.atan2(BY - p[1], BX - p[0]) - p[2]; b = math.atan2(math.sin(b), math.cos(b))
    if d <= RMAX and abs(b) <= FOV: t_in = (tt, d, math.degrees(b), p); break
rows = []
for tt, ox, oy, r, A in LC:
    ys, xs = np.nonzero(A >= 100); a = at(MO, MOt, tt); c, s = math.cos(a[2]), math.sin(a[2])
    px, py = ox + (xs + 0.5) * r, oy + (ys + 0.5) * r; X, Y = a[0] + c * px - s * py, a[1] + s * px + c * py
    rows.append((tt, int(np.sum((X >= X0) & (X <= X1) & (Y >= Y0) & (Y <= Y1)))))
print('bag %s · 로컬 코스트맵 %d 장 · 상자 중심 (%.2f, %.2f) 영역 x %.2f~%.2f y %.2f~%.2f' % (Path(bag).name, len(rows), BX, BY, X0, X1, Y0, Y1))
if not t_in:
    print('  t0 없음 — 상자가 1.4 m · ±40° 안에 든 적 없음'); sys.exit(0)
print('  t0 = %.2f s (로버 (%.2f, %.2f, %.0f°), 거리 %.2f m, 방위 %+.0f°)' % (t_in[0], t_in[3][0], t_in[3][1], math.degrees(t_in[3][2]), t_in[1], t_in[2]))
before = [n for tt, n in rows if tt < t_in[0]]
print('  t0 전 상자 칸 최대 %d (출발 전 기억)' % (max(before) if before else -1))
hit = next(((tt, n) for tt, n in rows if tt >= t_in[0] and n >= NEED), None)
print('  t0 뒤 처음 ≥ %d 칸: %s' % (NEED, 't %.2f s (%d 칸) · 지연 %.2f s' % (hit[0], hit[1], hit[0] - t_in[0]) if hit else '없음'))
win = [n for tt, n in rows if t_in[0] <= tt <= t_in[0] + 10]
print('  t0~t0+10 s 칸 수: 최대 %d · 중앙 %.0f · 시간순 %s' % (max(win) if win else -1, np.median(win) if win else -1, ' '.join(str(n) for n in win[:25])))
