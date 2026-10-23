#!/usr/bin/env python3
"""anal_cost_section — 상자 옆 단면(지도 x 고정)에서 로컬 코스트맵 비용을 y 따라(2026-10-23 §12, PC).
  왜: f2von2 영상 — 상자 옆에서 MPPI 최적 궤적이 경로 선(y ≈ 0.27)으로 올라가지 않고 y ≈ 0.17 로 곧게 감. 그 단면에서 비용이 어느 쪽에 낮은지.
  비용은 칸 중심값(0~100, 99 내접 · 100 치명), odom 코스트맵을 그 순간 map→odom 으로 옮겨 지도 좌표로. 차체 중심이 그 y 에 있을 때의 '중심 칸 비용' 과
  차체(반폭 0.165) 양 옆 끝 칸 비용도 함께.
  인자: bag 시각들(s, 쉼표) x값들(쉼표) [y0,y1=−0.05,0.70]"""
import sys, math, bisect
from pathlib import Path
import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
bag = sys.argv[1]; TQ = [float(v) for v in sys.argv[2].split(',')]; XS = [float(v) for v in sys.argv[3].split(',')]
Y0, Y1 = (float(v) for v in (sys.argv[4] if len(sys.argv) > 4 else '-0.05,0.70').split(','))
yq = lambda q: math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
MO, LC = [], []
with AnyReader([Path(bag)], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
    T0 = rd.start_time * 1e-9
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/tf', '/local_costmap/costmap')]):
        tt = t * 1e-9 - T0; m = rd.deserialize(raw, c.msgtype)
        if c.topic == '/tf':
            for tr in m.transforms:
                if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom': MO.append((tt, (tr.transform.translation.x, tr.transform.translation.y, yq(tr.transform.rotation))))
        elif min(TQ) - 1 <= tt <= max(TQ) + 1:
            g = m.info; LC.append((tt, g.origin.position.x, g.origin.position.y, g.resolution, np.array(m.data, np.int16).reshape(g.height, g.width)))
MO.sort(); MOt = [q[0] for q in MO]; LCt = [q[0] for q in LC]
last = lambda L, Lt, t: L[max(bisect.bisect_right(Lt, t) - 1, 0)]
YS = np.round(np.arange(Y0, Y1 + 1e-6, 0.05), 3)
print('bag %s · 로컬 코스트맵 단면 비용(칸 중심, 0~100) · 열 = 지도 y' % Path(bag).name)
print('  t · x     | ' + ' '.join('%5.2f' % y for y in YS))
for t in TQ:
    _, ox, oy, r, A = last(LC, LCt, t); mo = last(MO, MOt, t)[1]; c, s = math.cos(-mo[2]), math.sin(-mo[2])
    for x in XS:
        row = []
        for y in YS:
            dx, dy = x - mo[0], y - mo[1]; lx, ly = c * dx - s * dy, s * dx + c * dy; i, j = int((ly - oy) / r), int((lx - ox) / r)
            row.append(A[i, j] if 0 <= i < A.shape[0] and 0 <= j < A.shape[1] else -9)
        print('  %5.1f · %.2f | ' % (t, x) + ' '.join('%5d' % v for v in row))
