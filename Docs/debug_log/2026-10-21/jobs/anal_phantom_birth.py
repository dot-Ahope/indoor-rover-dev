#!/usr/bin/env python3
"""anal_phantom_birth — '카메라 층만' LETHAL 덩어리가 언제 생겼나: 상자 영역 안 칸이 처음 100 이 된 시각과 그때 로버 자세(거리 · 카메라 기준 방위). (2026-10-21 §13, PC)
  인자: bag 영역들 'x0,x1,y0,y1;...'   — 영역마다 칸별 첫 LETHAL 시각 분포, 그 시각들의 로버 위치 · 영역 중심까지 거리 · 방위(로버 앞 기준, 카메라 시야 ±43°)
  주의: 전역 코스트맵 = 지도 + nvblox + 라이다 층 합. 지도 칸(저장 지도 점유 0.10 m 안)은 빼고 본다."""
import sys, math, bisect
from pathlib import Path
import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
bag = sys.argv[1]; R = [[float(v) for v in s.split(',')] for s in sys.argv[2].split(';')]


def yaw(q): return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))


def comp(a, b):
    c, s = math.cos(a[2]), math.sin(a[2]); return (a[0] + c * b[0] - s * b[1], a[1] + s * b[0] + c * b[1], a[2] + b[2])


GC, MP, MO, OB = [], None, [], []
with AnyReader([Path(bag)], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
    t0 = rd.start_time * 1e-9
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/global_costmap/costmap', '/map', '/tf')]):
        m = rd.deserialize(raw, c.msgtype); tt = t * 1e-9 - t0
        if c.topic == '/tf':
            for tr in m.transforms:
                a = (tr.transform.translation.x, tr.transform.translation.y, yaw(tr.transform.rotation))
                if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom': MO.append((tt, a))
                elif tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link': OB.append((tt, a))
        else:
            g = m.info; A = np.array(m.data, dtype=np.int16).reshape(g.height, g.width)
            if c.topic == '/map': MP = (g.origin.position.x, g.origin.position.y, g.resolution, A)
            else: GC.append((tt, g.origin.position.x, g.origin.position.y, g.resolution, A))
at = lambda L, t: L[max(bisect.bisect_right([x[0] for x in L], t) - 1, 0)][1]
mx, my, mr, MA = MP; mys, mxs = np.nonzero(MA >= 65); MPt = np.c_[mx + (mxs + 0.5) * mr, my + (mys + 0.5) * mr]
print('bag %s · 전역 코스트맵 %d 장(%.1f Hz)' % (Path(bag).name, len(GC), len(GC) / (GC[-1][0] - GC[0][0])))
for x0, x1, y0, y1 in R:
    first = {}
    for tt, ox, oy, r, A in GC:
        ys, xs = np.nonzero(A >= 100); cx, cy = ox + (xs + 0.5) * r, oy + (ys + 0.5) * r
        k = (cx >= x0) & (cx <= x1) & (cy >= y0) & (cy <= y1)
        for px, py in zip(cx[k], cy[k]):
            key = (round(px, 2), round(py, 2))
            if key in first: continue
            if np.hypot(MPt[:, 0] - px, MPt[:, 1] - py).min() <= 0.10: first[key] = None; continue   # 지도 칸
            first[key] = tt
    ts = sorted(v for v in first.values() if v is not None)
    print('\n영역 x %.2f~%.2f y %.2f~%.2f: 지도 밖 LETHAL 칸 %d 개 (지도 칸 %d)' % (x0, x1, y0, y1, len(ts), sum(v is None for v in first.values())))
    if not ts: continue
    cxm, cym = (x0 + x1) / 2, (y0 + y1) / 2
    # 처음 생긴 시각을 2 s 묶음으로
    bins = {}
    for v in ts: bins.setdefault(int(v // 2) * 2, []).append(v)
    for b in sorted(bins):
        P = comp(at(MO, b + 1), at(OB, b + 1)); d = math.hypot(cxm - P[0], cym - P[1])
        brg = math.degrees(math.atan2(cym - P[1], cxm - P[0]) - P[2]); brg = (brg + 180) % 360 - 180
        print('  t %3d~%3d s: 새 칸 %3d · 로버 (%.2f, %.2f, %4.0f°) · 영역 중심까지 %.2f m · 방위 %+4.0f°%s' % (b, b + 2, len(bins[b]), P[0], P[1], math.degrees(P[2]), d, brg, '' if abs(brg) <= 43 else ' (카메라 시야 밖)'))
