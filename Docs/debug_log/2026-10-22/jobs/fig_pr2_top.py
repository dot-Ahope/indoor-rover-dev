#!/usr/bin/env python3
"""fig_pr2_top — 정지 프리셋 시험 복셀(base_link 기준 5 cm, 띠 0.06~0.30 m 를 위에서 합침)을 10-21 pr1_top.png 처럼 나란히(2026-10-22 §14, PC).
  색 = 찍힌 프레임 비율(열마다 높이 중 최대): 초록 ≥ 80 % · 노랑 30~80 % · 주황 < 30 %. 흰 테두리 = 상자(로버 기준 x 1.15~1.26, y −0.20~−0.02 — 출발 자세 = 지도 원점), 호 = 1.4 m.
  인자: 출력.png 이름=npz ..."""
import sys, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Arc
plt.rcParams['font.family'] = 'Malgun Gothic'; plt.rcParams['axes.unicode_minus'] = False
out = sys.argv[1]; R = [a.split('=') for a in sys.argv[2:]]; V = 0.05
fig, axs = plt.subplots(1, len(R), figsize=(3.4 * len(R), 3.6), facecolor='#202020')
for ax, (nm, f) in zip(axs, R):
    z = np.load(f); col = {}
    for (i, j, k), fr in zip(z['keys'], z['frac']): col[(i, j)] = max(col.get((i, j), 0), fr)
    ax.set_facecolor('#202020'); n = {'g': 0, 'y': 0, 'o': 0}
    for (i, j), fr in col.items():
        c, k = ('#43b04a', 'g') if fr >= .8 else (('#f2c919', 'y') if fr >= .3 else ('#ff8c42', 'o')); n[k] += 1
        ax.add_patch(Rectangle((i * V, j * V), V, V, color=c, lw=0))
    ax.add_patch(Rectangle((1.151, -0.20), 0.11, 0.18, fill=False, ec='white', lw=1.2)); ax.add_patch(Arc((0, 0), 2.8, 2.8, theta1=-50, theta2=50, ec='#777777', lw=0.8))
    ax.set_xlim(0.3, 1.6); ax.set_ylim(-0.75, 0.75); ax.set_aspect('equal'); ax.tick_params(colors='#aaaaaa', labelsize=7)
    for s in ax.spines.values(): s.set_color('#444444')
    ax.set_title('%s\n안정 %d · 중간 %d · 깜빡 %d (위에서 본 열)' % (nm, n['g'], n['y'], n['o']), color='white', fontsize=9)
fig.text(0.5, 0.01, '초록 ≥80 % · 노랑 30~80 % · 주황 <30 % · 흰 테두리 = 상자 · 호 = 1.4 m · 로버 기준 x 앞 · y 왼쪽', color='#cccccc', ha='center', fontsize=8)
plt.tight_layout(rect=(0, 0.04, 1, 1)); plt.savefig(out, dpi=130, facecolor=fig.get_facecolor()); print('그림', out)
