#!/usr/bin/env python3
"""fig_box_zoom_cmp — 두 주행의 출발점 시험 상자 확대: nvblox 조각의 표면 안 칸(지도 좌표)을 출발 길 · 복귀 길 통과 순간마다 나란히. (2026-10-19 §21)
  왜: f2y1(번갈이) 복귀 길 서쪽 면 과장 +18.2 cm(f2x1 +0.4) — 상자가 부푼 것인지, 상자와 떨어진 칸인지 눈으로.
  통과 순간 = 로버가 상자 옆 구간(anal_slice_box 와 같은 조건: 지도 x 0.9~1.7, |y| < 0.6)에 머문 동안 상자 중심에 가장 가까웠던 조각.
  칸 색 = 그 조각에서의 거리(≤ 0 = 표면 안). 인자: 출력.png 이름=주행bag ..."""
import sys, math, bisect
from pathlib import Path
import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore, get_types_from_msg
plt.rcParams['font.family'] = 'Malgun Gothic'; plt.rcParams['axes.unicode_minus'] = False
TS = get_typestore(Stores.ROS2_HUMBLE)
TS.register(get_types_from_msg('std_msgs/Header header\nfloat32 resolution\nuint32 width\nuint32 height\ngeometry_msgs/Point origin\nfloat32 unknown_value\nfloat32[] data\n', 'nvblox_msgs/msg/DistanceMapSlice'))
BOX = (1.151, 1.261, -0.20, -0.02); ZR = (0.6, 1.8, -0.75, 0.45); REG = (0.95, 1.50, -0.25, 0.25)
FP = np.array([[0.262, 0.165], [0.262, -0.165], [-0.248, -0.165], [-0.248, 0.165]])
yq = lambda q: math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
comp = lambda A, B: (A[0] + math.cos(A[2]) * B[0] - math.sin(A[2]) * B[1], A[1] + math.sin(A[2]) * B[0] + math.cos(A[2]) * B[1], A[2] + B[2])
out = sys.argv[1]; runs = [a.split('=') for a in sys.argv[2:]]
fig, axs = plt.subplots(len(runs), 2, figsize=(10, 5 * len(runs)))
for ri, (nm, bag) in enumerate(runs):
    MO, OB, SL = [], [], []
    with AnyReader([Path(bag)], default_typestore=TS) as rd:
        for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/tf', '/nvblox_node/static_map_slice')]):
            m = rd.deserialize(raw, c.msgtype)
            if c.topic == '/tf':
                for tr in m.transforms:
                    st = tr.header.stamp.sec + tr.header.stamp.nanosec * 1e-9; v = (tr.transform.translation.x, tr.transform.translation.y, yq(tr.transform.rotation))
                    if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom': MO.append((st, v))
                    elif tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link': OB.append((st, v))
            else: SL.append(m)
    MO.sort(); OB.sort(); MOt = [q[0] for q in MO]; OBt = [q[0] for q in OB]; t0 = MOt[0]
    at = lambda L, T, t: L[max(bisect.bisect_right(T, t) - 1, 0)][1]
    near = []
    for m in SL:
        st = m.header.stamp.sec + m.header.stamp.nanosec * 1e-9; P = comp(at(MO, MOt, st), at(OB, OBt, st))
        if 0.9 <= P[0] <= 1.7 and abs(P[1]) < 0.6: near.append((st, m, P))
    T = [q[0] for q in near]; cuts = [0] + [i for i in range(1, len(T)) if T[i] - T[i - 1] > 5] + [len(T)]
    for si, (a, b) in enumerate(list(zip(cuts, cuts[1:]))[:2]):
        seg = near[a:b]; st, m, P = min(seg, key=lambda q: math.hypot(q[2][0] - 1.206, q[2][1] + 0.11))
        mo = at(MO, MOt, st); d = np.array(m.data, np.float32).reshape(m.height, m.width); r = m.resolution
        iy, ix = np.nonzero(d != m.unknown_value); lx = m.origin.x + (ix + 0.5) * r; ly = m.origin.y + (iy + 0.5) * r
        gx = mo[0] + math.cos(mo[2]) * lx - math.sin(mo[2]) * ly; gy = mo[1] + math.sin(mo[2]) * lx + math.cos(mo[2]) * ly; dv = d[iy, ix]
        ax = axs[ri, si]; z = (gx > ZR[0] - 0.05) & (gx < ZR[1] + 0.05) & (gy > ZR[2] - 0.05) & (gy < ZR[3] + 0.05)
        occ = z & (dv <= 0); near_ = z & (dv > 0) & (dv < 0.10)
        for X, Y in zip(gx[near_], gy[near_]): ax.add_patch(Rectangle((X - r / 2, Y - r / 2), r, r, angle=math.degrees(mo[2]), rotation_point='center', color='#f5c6a5', lw=0))
        for X, Y in zip(gx[occ], gy[occ]): ax.add_patch(Rectangle((X - r / 2, Y - r / 2), r, r, angle=math.degrees(mo[2]), rotation_point='center', color='#d62728', lw=0))
        ax.add_patch(Rectangle((BOX[0], BOX[2]), BOX[1] - BOX[0], BOX[3] - BOX[2], fill=False, ec='#1f4fa8', lw=2, label='실제 상자'))
        x, y, th = P; ax.add_patch(Polygon([(x + math.cos(th) * p - math.sin(th) * q, y + math.sin(th) * p + math.cos(th) * q) for p, q in FP], fill=False, ec='#2c8a2c', lw=2, label='차체'))
        k = (gx > REG[0]) & (gx < REG[1]) & (gy > REG[2]) & (gy < REG[3]) & (dv <= 0)
        nb = 100 * (gy[k].max() + r / 2 - BOX[3]) if k.any() else float('nan'); wb = 100 * (BOX[0] - (gx[k].min() - r / 2)) if k.any() else float('nan')
        ax.set_xlim(ZR[0], ZR[1]); ax.set_ylim(ZR[2], ZR[3]); ax.set_aspect('equal'); ax.grid(alpha=0.3)
        ax.set_title('%s %s t=%.1f s · 북 %+.1f · 서 %+.1f cm · 표면 안 칸 %d' % (nm, ['출발 길', '복귀 길'][si], st - t0, nb, wb, int(occ.sum())), fontsize=10)
        if ri == 0 and si == 0: ax.legend(fontsize=8, loc='lower left')
fig.suptitle('출발점 시험 상자 근처 nvblox 조각(빨강 = 표면 안 칸, 살구 = 10 cm 안) — 통과 순간', fontsize=12); fig.tight_layout()
fig.savefig(out, dpi=110); print('그림', out)
