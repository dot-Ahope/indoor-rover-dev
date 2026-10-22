#!/usr/bin/env python3
"""fig_box_cells — 출발점 낮은 상자 둘레의 nvblox 장애물 칸을 위에서 본 그림(10-21 pr1_top.png 의 주행판, 2026-10-22 §10, PC).
  칸 = 조각(/nvblox_node/static_map_slice) 거리 ≤ 0 을 지도 0.05 m 칸으로. 색 = 창 안 조각 중 그 칸이 장애물이었던 비율:
  초록 ≥ 80 %(안정) · 노랑 30~80 % · 주황 < 30 %(깜빡). 흰 테두리 = 기록 상자(10-19 실측), 옅은 회색 = 저장 지도 벽, 회색 점선 = 맨바닥 영역 A.
  창: ① 출발 — 상자 t0 ~ t0+10 s ② 출발 길 — t 10~60 s(상자 옆 → 동쪽, 맨바닥 유령이 생기는 구간 — 10-21 정의) ③ 복귀 — t > 120 s 이고 로버가 상자 중심 1.2 m 안.
  인자: 출력.png 이름=주행bag[@조각bag]@t0 ...   (조각bag 생략 = 주행 bag 의 실시간 조각)"""
import sys, math, bisect
from pathlib import Path
import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore, get_types_from_msg
plt.rcParams['font.family'] = 'Malgun Gothic'; plt.rcParams['axes.unicode_minus'] = False
TS = get_typestore(Stores.ROS2_HUMBLE)
TS.register(get_types_from_msg('std_msgs/Header header\nfloat32 resolution\nuint32 width\nuint32 height\ngeometry_msgs/Point origin\nfloat32 unknown_value\nfloat32[] data\n', 'nvblox_msgs/msg/DistanceMapSlice'))
BOX = (1.151, 1.261, -0.20, -0.02); BC = ((BOX[0] + BOX[1]) / 2, (BOX[2] + BOX[3]) / 2); ZA = (1.45, 2.65, -0.35, 0.45)
X0, X1, Y0, Y1 = 0.6, 2.8, -1.0, 1.2; C = 0.05
yq = lambda q: math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
def comp(a, b):
    c, s = math.cos(a[2]), math.sin(a[2]); return (a[0] + c * b[0] - s * b[1], a[1] + s * b[0] + c * b[1], a[2] + b[2])
out = sys.argv[1]; runs = []
for arg in sys.argv[2:]:
    nm, rest = arg.split('='); parts = rest.split('@'); drive, t0b = parts[0], float(parts[-1]); sl = parts[1] if len(parts) == 3 else drive
    MO, OB, MAP = [], [], None
    with AnyReader([Path(drive)], default_typestore=TS) as rd:
        T0 = rd.start_time * 1e-9
        for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/tf', '/map')]):
            m = rd.deserialize(raw, c.msgtype)
            if c.topic == '/map': MAP = m; continue
            for tr in m.transforms:
                st = tr.header.stamp.sec + tr.header.stamp.nanosec * 1e-9; v = (tr.transform.translation.x, tr.transform.translation.y, yq(tr.transform.rotation))
                if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom': MO.append((st, v))
                elif tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link': OB.append((st, v))
    MO.sort(); OB.sort(); MOt = [q[0] for q in MO]; OBt = [q[0] for q in OB]
    at = lambda L, Lt, t: L[max(bisect.bisect_right(Lt, t) - 1, 0)][1]
    W = {'start': [], 'go': [], 'ret': []}
    with AnyReader([Path(sl)], default_typestore=TS) as rd:
        for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic == '/nvblox_node/static_map_slice']):
            m = rd.deserialize(raw, c.msgtype); st = m.header.stamp.sec + m.header.stamp.nanosec * 1e-9; tt = st - T0
            p = comp(at(MO, MOt, st), at(OB, OBt, st)); near = math.hypot(p[0] - BC[0], p[1] - BC[1]) < 1.2
            keys = [k for k, ok in (('start', t0b <= tt <= t0b + 10), ('go', 10 <= tt <= 60), ('ret', tt > 120 and near)) if ok]
            if not keys: continue
            mo = (0.0, 0.0, 0.0) if m.header.frame_id == 'map' else at(MO, MOt, st)
            d = np.array(m.data, np.float32).reshape(m.height, m.width); iy, ix = np.nonzero((d <= 0) & (d != m.unknown_value)); r = m.resolution
            lx = m.origin.x + (ix + 0.5) * r; ly = m.origin.y + (iy + 0.5) * r
            gx = mo[0] + math.cos(mo[2]) * lx - math.sin(mo[2]) * ly; gy = mo[1] + math.sin(mo[2]) * lx + math.cos(mo[2]) * ly
            cells = set(zip(np.floor(gx / C).astype(int), np.floor(gy / C).astype(int)))
            for key in keys: W[key].append((tt, p, cells))
    runs.append((nm, MAP, W))
WN = (('start', '출발 t0~t0+10 s'), ('go', '출발 길 t 10~60 s'), ('ret', '복귀 상자 1.2 m 안'))
fig, axs = plt.subplots(3, len(runs), figsize=(4.2 * len(runs), 12.6), facecolor='#202020')
axs = np.atleast_2d(axs).reshape(3, len(runs))
for j, (nm, MAP, W) in enumerate(runs):
    for i, (key, win) in enumerate(WN):
        ax = axs[i, j]; ax.set_facecolor('#202020'); fr = W[key]
        if MAP is not None:
            g = np.array(MAP.data).reshape(MAP.info.height, MAP.info.width); yy, xx = np.nonzero(g >= 65); r = MAP.info.resolution
            ax.scatter(MAP.info.origin.position.x + (xx + .5) * r, MAP.info.origin.position.y + (yy + .5) * r, s=2, c='#555555', marker='s', lw=0)
        cnt = {}
        for _, _, s in fr:
            for k in s: cnt[k] = cnt.get(k, 0) + 1
        n = max(len(fr), 1); stat = {'g': 0, 'y': 0, 'o': 0}
        for (a, b), v in cnt.items():
            f = v / n; col, k = ('#43b04a', 'g') if f >= .8 else (('#f2c919', 'y') if f >= .3 else ('#ff8c42', 'o'))
            x, y = a * C, b * C
            if X0 <= x <= X1 and Y0 <= y <= Y1: ax.add_patch(Rectangle((x, y), C, C, color=col, lw=0)); stat[k] += 1
        ax.add_patch(Rectangle((BOX[0], BOX[2]), BOX[1] - BOX[0], BOX[3] - BOX[2], fill=False, ec='white', lw=1.4))
        ax.add_patch(Rectangle((ZA[0], ZA[2]), ZA[1] - ZA[0], ZA[3] - ZA[2], fill=False, ec='#888888', lw=0.8, ls='--'))
        if fr:
            P = np.array([q[1][:2] for q in fr]); ax.plot(P[:, 0], P[:, 1], color='#4aa3ff', lw=1.2)
        ax.set_xlim(X0, X1); ax.set_ylim(Y0, Y1); ax.set_aspect('equal'); ax.tick_params(colors='#aaaaaa', labelsize=7)
        for s_ in ax.spines.values(): s_.set_color('#444444')
        ax.set_title('%s · %s\n조각 %d · 안정 %d · 중간 %d · 깜빡 %d' % (nm, win, len(fr), stat['g'], stat['y'], stat['o']), color='white', fontsize=9)
fig.text(0.5, 0.01, '초록 ≥80 % · 노랑 30~80 % · 주황 <30 %(창 안 조각 중 장애물이었던 비율) · 흰 테두리 = 상자 · 점선 = 맨바닥 영역 A · 파란 선 = 로버 궤적 · 회색 = 저장 지도 벽', color='#cccccc', ha='center', fontsize=8)
plt.tight_layout(rect=(0, 0.02, 1, 1)); plt.savefig(out, dpi=130, facecolor=fig.get_facecolor()); print('그림', out)
