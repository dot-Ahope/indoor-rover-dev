#!/usr/bin/env python3
"""fig_box_compare — 복귀 길 상자 옆을 B0(NavFn) 주행과 Smac 주행으로 나란히: 지나간 길 · 차체 자국 · 그때 따른 전역 경로 · 실제 최소 여유 (2026-10-26 §8, PC).
  왜: 사용자 — "이전 2번의 주행 시각화해달라". 상자 옆 여유가 계획 경로에서 왔는지 · 컨트롤러 추종에서 잃었는지를 한 장에서 보려고.
  데이터: 각 bag 의 /tf(map→odom ∘ odom→base_link), /plan(·/plan_smoothed). 복귀 구간 = 로버가 상자 둘레(x 0.5~2.3, y −0.6~0.8)에 들어온 마지막 덩어리.
    경로: 그 구간 시작 직전에 받은 BT 경로 — B0 는 /plan_smoothed(없으면 /plan 의 점 간격 ≤ 0.04), Smac 은 /plan 중 점 간격 > 0.04 m(러너 조회 NavFn 0.025 제외).
    여유 = 차체 직사각형(0.262/−0.248 × ±0.165) ↔ 기록 상자(x 1.151~1.261, y −0.20~−0.02) 최소 거리.
  인자: 출력.png 이름=bag폴더 ...(앞 3 개 B0, 뒤는 Smac — 이름에 'sh' 있으면 Smac)"""
import sys, math, bisect
from pathlib import Path
import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
plt.rcParams.update({'font.family': 'Malgun Gothic', 'axes.unicode_minus': False})
BOX = (1.151, 1.261, -0.20, -0.02); FP = np.array([[0.262, 0.165], [0.262, -0.165], [-0.248, -0.165], [-0.248, 0.165]])
yq = lambda q: math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
def comp(a, b):
    c, s = math.cos(a[2]), math.sin(a[2]); return (a[0] + c * b[0] - s * b[1], a[1] + s * b[0] + c * b[1], a[2] + b[2])
BP = np.array([[x, y] for x in np.linspace(BOX[0], BOX[1], 12) for y in np.linspace(BOX[2], BOX[3], 19)])
def clr(p):
    c, s = math.cos(p[2]), math.sin(p[2]); d = BP - p[:2]; bx = c * d[:, 0] + s * d[:, 1]; by = -s * d[:, 0] + c * d[:, 1]
    return float(np.hypot(np.maximum(np.maximum(-0.248 - bx, bx - 0.262), 0), np.maximum(np.maximum(-0.165 - by, by - 0.165), 0)).min())


def load(bag):
    MO, OB, PL = [], [], []
    with AnyReader([Path(bag)], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
        for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/tf', '/plan', '/plan_smoothed')]):
            m = rd.deserialize(raw, c.msgtype); ts = t * 1e-9
            if c.topic == '/tf':
                for tr in m.transforms:
                    v = (tr.transform.translation.x, tr.transform.translation.y, yq(tr.transform.rotation))
                    if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom': MO.append((ts, v))
                    elif tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link': OB.append((ts, v))
            elif len(m.poses) > 3:
                P = np.array([[p.pose.position.x, p.pose.position.y] for p in m.poses]); PL.append((ts, c.topic, P, float(np.median(np.hypot(*np.diff(P, axis=0).T)))))
    for L in (MO, OB): L.sort(key=lambda q: q[0])
    at = lambda L, T, t: L[max(bisect.bisect_right(T, t) - 1, 0)][1]; MOt = [q[0] for q in MO]; OBt = [q[0] for q in OB]
    T = np.arange(OB[0][0], OB[-1][0], 0.1); P = np.array([comp(at(MO, MOt, t), at(OB, OBt, t)) for t in T])
    inside = (P[:, 0] > 0.5) & (P[:, 0] < 2.3) & (P[:, 1] > -0.6) & (P[:, 1] < 0.8)
    idx = np.nonzero(inside)[0]; brk = np.nonzero(np.diff(idx) > 5)[0]; seg = idx[brk[-1] + 1:] if len(brk) else idx   # 마지막 덩어리 = 복귀
    return T, P, seg, PL


runs = [a.split('=', 1) for a in sys.argv[2:]]
fig, axs = plt.subplots(1, 2, figsize=(16, 7.2), sharex=True, sharey=True)
cols = ['#5b3cc4', '#0f766e', '#c2255c', '#e8590c', '#1c7ed6']
rows = {0: [], 1: []}
for k, (name, bag) in enumerate(runs):
    smac = 'sh' in name; ax = axs[1 if smac else 0]; col = cols[k % len(cols)]
    T, P, seg, PL = load(bag)
    C = np.array([clr(p) for p in P[seg]]); i = int(np.argmin(C)); pm = P[seg][i]; tmin = T[seg][i]
    # 점선 = 최소 여유 순간에 쓰이던 BT 경로(그 시각 이전 마지막). 첫 판은 복귀 구간 시작 직전 경로를 그려 B0 는 막힘 전 '상자 관통' 경로가 나왔음
    cand = [q for q in PL if q[0] <= tmin and ((q[3] > 0.04) if smac else (q[1] == '/plan_smoothed' or q[3] <= 0.04))]
    path = cand[-1][2] if cand else None
    if path is not None: ax.plot(path[:, 0], path[:, 1], color=col, lw=1.4, ls='--', alpha=0.9)
    ax.plot(P[seg, 0], P[seg, 1], color=col, lw=2.2, label='%s  최소 %.1f cm' % (name, 100 * C[i]))
    for j in seg[::8]:
        c, s = math.cos(P[j, 2]), math.sin(P[j, 2]); W = np.c_[P[j, 0] + c * FP[:, 0] - s * FP[:, 1], P[j, 1] + s * FP[:, 0] + c * FP[:, 1]]
        ax.add_patch(Polygon(W, closed=True, fc='none', ec=col, lw=0.5, alpha=0.35))
    c, s = math.cos(pm[2]), math.sin(pm[2]); W = np.c_[pm[0] + c * FP[:, 0] - s * FP[:, 1], pm[1] + s * FP[:, 0] + c * FP[:, 1]]
    ax.add_patch(Polygon(W, closed=True, fc=col, ec=col, lw=1.8, alpha=0.25)); ax.plot(*pm[:2], 'o', color=col, ms=5)
    rows[1 if smac else 0].append((name, 100 * C[i]))
for ax, ttl in zip(axs, ('B0 · NavFn (f2rp1 · f2rp2 · f2rp5, 10-23)', 'Smac Hybrid RS (f2sh1 · f2sh2, 10-26)')):
    ax.add_patch(Rectangle((BOX[0], BOX[2]), BOX[1] - BOX[0], BOX[3] - BOX[2], fc='#e03131', ec='#1f2328', lw=1.0, zorder=5))
    ax.set_xlim(0.3, 2.4); ax.set_ylim(-0.75, 0.85); ax.set_aspect('equal'); ax.grid(color='#e5e7eb', lw=0.6)
    ax.set_title(ttl, loc='left', fontsize=13); ax.legend(loc='upper left', fontsize=10, frameon=False); ax.set_xlabel('map x (m)')
axs[0].set_ylabel('map y (m)')
fig.suptitle('복귀 길 상자(빨강) 옆 — 실선 = 지나간 길(로버 중심), 점선 = 가장 가까운 순간에 따르던 전역 경로, 칠한 차체 = 상자와 가장 가까운 순간', x=0.02, ha='left', fontsize=12)
fig.tight_layout(); fig.savefig(sys.argv[1], dpi=110)
for g, r in rows.items(): print(('Smac' if g else 'B0'), ' · '.join('%s %.1f cm' % q for q in r))
