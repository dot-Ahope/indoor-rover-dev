#!/usr/bin/env python3
"""fig_tolcp_paths — §5 허용치 · cost_penalty 재질의에서 새로 성공한 경로 모양 (2026-10-27, PC). 인자: tolcp폴더 장면.npz 그림.png"""
import sys, math, json
from pathlib import Path
import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.patches import Polygon
plt.rcParams.update({'font.family': 'Malgun Gothic', 'axes.unicode_minus': False})
O = Path(sys.argv[1]); SC = np.load(sys.argv[2])
FP = np.array([[0.262, 0.165], [0.262, -0.165], [-0.248, -0.165], [-0.248, 0.165]])
fp = lambda x, y, a: np.c_[x + math.cos(a) * FP[:, 0] - math.sin(a) * FP[:, 1], y + math.sin(a) * FP[:, 0] + math.cos(a) * FP[:, 1]]
cmap = ListedColormap(np.r_[np.linspace([1, 1, 1], [0.78, 0.80, 0.84], 99), [[0.45, 0.47, 0.52]], [[0.08, 0.09, 0.11]], [[0.98, 0.95, 0.80]]])
P = [('sa3_115653', 'V1', 30, '16:11:56.85 남행 · tol 0.35 · cp 3.0', None), ('sa3_115653', 'V3', 15, '16:11:56.85 남행 · tol 0.25 · cp 1.5', None),
     ('sa3_125954', 'V3', 15, '16:12:59.54 북행 · tol 0.25 · cp 1.5(전체 지도)', 'all')]
fig, axs = plt.subplots(1, 3, figsize=(16, 7.5), gridspec_kw={'width_ratios': [1, 1, 2.2]})
for ax, (k, v, cp, ttl, zoom) in zip(axs, P):
    R = np.load(O / ('result_%s.npz' % v)); ox, oy, r, _ = SC[k + '/info']; G = R[k + '/recon'].astype(np.int16); G = np.where(G < 0, 101, G)
    ax.imshow(G, origin='lower', extent=(ox, ox + G.shape[1] * r, oy, oy + G.shape[0] * r), cmap=cmap, vmin=0, vmax=101, interpolation='nearest')
    p = R['%s/Smac_R10_C%d_A10_RS/path' % (k, cp)]; nf = R['%s/GridBased/path' % k]; st, gl = SC[k + '/start'], SC[k + '/goal']
    ax.plot(nf[:, 0], nf[:, 1], color='#e8590c', ls='--', lw=1.4, label='NavFn')
    ax.plot(p[:, 0], p[:, 1], color='#0f9d58', lw=2.2, label='Smac(%.2f m)' % np.hypot(*np.diff(p[:, :2], axis=0).T).sum())
    for q in p[::max(1, len(p) // 12)]: ax.add_patch(Polygon(fp(*q), closed=True, fc='none', ec='#0f9d58', lw=0.6, alpha=0.6))
    ax.add_patch(Polygon(fp(*p[-1]), closed=True, fc='#0f9d58', ec='#0f9d58', alpha=0.3))
    ax.add_patch(Polygon(fp(*st), closed=True, fc='#1c7ed6', alpha=0.35)); ax.add_patch(Polygon(fp(*gl), closed=True, fc='none', ec='#c2255c', ls='--', lw=1.4))
    if zoom is None: ax.set_xlim(-2.25, -0.95); ax.set_ylim(-5.85, -3.25)
    ax.set_aspect('equal'); ax.set_xticks([]); ax.set_yticks([]); ax.set_title(ttl, fontsize=11, loc='left'); ax.legend(fontsize=8.5, loc='lower left')
fig.suptitle('허용치 · cost_penalty 를 바꿔 새로 성공한 Smac 경로(초록, 칠한 차체 = 경로 끝) · 파랑 = 출발, 분홍 점선 = 목표, 주황 점선 = NavFn', x=0.01, ha='left', fontsize=11.5)
fig.tight_layout(rect=(0, 0, 1, 0.95)); fig.savefig(sys.argv[3], dpi=110); print('저장', sys.argv[3])
