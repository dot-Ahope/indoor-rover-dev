#!/usr/bin/env python3
"""anal_door_pass — 전역 코스트맵에서 로버 → 목표로 '통과 가능한 칸'(값 < 99, 99 = INSCRIBED · 100 = LETHAL)만 밟아 닿는지(4-이웃 BFS), 문 줄(y 고정) 의 칸 값(2026-10-22 §6, PC).
  왜: f2dr1 목표 1 에서 계획기가 'failed to create plan' 반복 → 문이 코스트맵에서 막혔는지 직접 본다.
  인자: bag 시각들(s, 쉼표) 목표x,y 문줄y 문x0,x1"""
import sys, math, bisect
from collections import deque
from pathlib import Path
import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
bag = sys.argv[1]; TQ = [float(v) for v in sys.argv[2].split(',')]; GX, GY = (float(v) for v in sys.argv[3].split(','))
DY = float(sys.argv[4]); DX0, DX1 = (float(v) for v in sys.argv[5].split(','))
yaw = lambda q: math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
def comp(a, b):
    c, s = math.cos(a[2]), math.sin(a[2]); return (a[0] + c * b[0] - s * b[1], a[1] + s * b[0] + c * b[1], a[2] + b[2])
GC, MO, OB = [], [], []
with AnyReader([Path(bag)], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
    t0 = rd.start_time * 1e-9
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/global_costmap/costmap', '/tf')]):
        tt = t * 1e-9 - t0; m = rd.deserialize(raw, c.msgtype)
        if c.topic == '/tf':
            for tr in m.transforms:
                a = (tr.transform.translation.x, tr.transform.translation.y, yaw(tr.transform.rotation))
                if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom': MO.append((tt, a))
                elif tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link': OB.append((tt, a))
        else:
            g = m.info; GC.append((tt, g.origin.position.x, g.origin.position.y, g.resolution, np.array(m.data, dtype=np.int16).reshape(g.height, g.width)))
for L in (MO, OB): L.sort(key=lambda q: q[0])
at = lambda L, t: L[max(bisect.bisect_right([q[0] for q in L], t) - 1, 0)][1]
print('bag %s · 전역 코스트맵 %d 장 · 목표 (%.2f, %.2f) · 문 줄 y %.2f x %.2f~%.2f' % (Path(bag).name, len(GC), GX, GY, DY, DX0, DX1))
for tq in TQ:
    k = max(bisect.bisect_right([q[0] for q in GC], tq) - 1, 0); tt, ox, oy, r, A = GC[k]
    p = comp(at(MO, tt), at(OB, tt)); ij = lambda x, y: (int((y - oy) / r), int((x - ox) / r))
    s, g = ij(p[0], p[1]), ij(GX, GY); free = A < 99
    seen = np.zeros_like(free); q = deque([s]); seen[s] = True
    while q:
        i, j = q.popleft()
        for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            a, b = i + di, j + dj
            if 0 <= a < A.shape[0] and 0 <= b < A.shape[1] and free[a, b] and not seen[a, b]: seen[a, b] = True; q.append((a, b))
    di = ij(0, DY)[0]; row = [A[di, ij(x, DY)[1]] for x in np.arange(DX0, DX1 + 1e-6, r)]
    print(' t %.1f s 장 %.1f · 로버 (%.2f, %.2f) 칸값 %d · 목표 칸값 %d · 통과 칸으로 닿음 %s · 문 줄 값 %s' % (tq, tt, p[0], p[1], A[s], A[g], '예' if seen[g] else '아니오', ' '.join(str(v) for v in row)))
