#!/usr/bin/env python3
"""fig_box_dump — 시험 상자 둘레 세 층(카메라 깊이 점군 · nvblox 거리 지도 · 로컬 코스트맵)을 site 2.0 / 1.0 두 조건 나란히, 실제 상자 위치와 함께. (2026-10-15 §23, 오늘만)
  입력: chk_box_dump.py 가 Jetson 에서 저장한 npz 두 개(정지, 출발 테이프).
  실제 상자: 사용자 줄자 — 차체 앞끝(base_link + 0.262 m)에서 서쪽 면까지 0.92 m(10-15 §22.2). 크기 18(폭, y) × 11(깊이, x) × 14(높이) cm,
            중심 y 는 시험 코스 문서 §1 기록 −0.07~−0.11(오늘 미측정) → 그 범위를 옅게.
  그림(판마다, 위에서 본 지도 좌표): 회색 점 = 깊이 점군 중 높이 0.06~0.30 m(카메라 지도가 장애물로 쓰는 높이), 주황 칸 = 거리 지도 ≤ 0(카메라가 점유로 본 칸),
       연한 주황 = 거리 0~5 cm, 빨간 테 = 코스트맵 치명 칸, 초록 실선 = 실제 상자 앞면, 초록 점선 상자 = 기록상 상자 범위.
  아래 표: 행(y)마다 서쪽 면 x — 점군 5 % 분위 · 거리 지도 · 코스트맵, 그리고 실제 면과의 차.
  인자: A.npz B.npz 출력.png"""
import sys, math
import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
plt.rcParams['font.family'] = 'Malgun Gothic'; plt.rcParams['axes.unicode_minus'] = False
fa, fb, out = sys.argv[1:4]; R0 = 0.05
fig = plt.figure(figsize=(14, 11)); gs = fig.add_gridspec(2, 2, height_ratios=[1.6, 1], hspace=0.25, wspace=0.12)
rows_all = []
for i, (f, lab) in enumerate(((fa, 'A · site 2.0 (기준선 구성)'), (fb, 'B · site 1.0 (라이브러리 기본)'))):
    D = np.load(f, allow_pickle=True); P = D['pts']; S = D['slice']; L = D['lc']; rx, ry, ryaw = D['robot']
    front = rx + 0.262 * math.cos(ryaw); truth = front + 0.92
    ax = fig.add_subplot(gs[0, i]); ax.set_facecolor('#f7f8fa')
    band = (P[:, 2] >= 0.06) & (P[:, 2] <= 0.30); Q = P[band]
    if len(Q) > 40000: Q = Q[np.random.default_rng(0).choice(len(Q), 40000, replace=False)]
    ax.scatter(Q[:, 0], Q[:, 1], s=0.4, color='#6b7680', alpha=0.35, lw=0, zorder=2)
    for x, y, d in S:
        if d <= 0: ax.add_patch(Rectangle((x - R0 / 2, y - R0 / 2), R0, R0, fc='#e07b24', ec='none', alpha=0.75, zorder=1))
        elif d <= 0.05: ax.add_patch(Rectangle((x - R0 / 2, y - R0 / 2), R0, R0, fc='#f6c48f', ec='none', alpha=0.6, zorder=1))
    for x, y, v in L:
        if v >= 100: ax.add_patch(Rectangle((x - R0 / 2, y - R0 / 2), R0, R0, fc='none', ec='#c53030', lw=1.8, zorder=3))
    ax.axvline(truth, color='#2f855a', lw=2.2, zorder=4); ax.text(truth + 0.005, 0.17, '실제 앞면 x %.3f\n(앞끝 %.3f + 0.92)' % (truth, front), color='#2f855a', fontsize=9, va='top')
    ax.add_patch(Rectangle((truth, -0.11 - 0.09), 0.11, 0.18, fc='none', ec='#2f855a', ls='--', lw=1.2, zorder=4))
    ax.add_patch(Rectangle((truth, -0.07 - 0.09), 0.11, 0.18, fc='none', ec='#2f855a', ls=':', lw=1.0, zorder=4))
    ax.set_xlim(0.95, 1.40); ax.set_ylim(-0.32, 0.18); ax.set_aspect('equal'); ax.grid(color='#c9d1d9', lw=0.4)
    nocc = int((S[:, 2] <= 0).sum()); nl = int((L[:, 2] >= 100).sum())
    ax.set_title('%s\n로버 지도 (%.3f, %.3f, %+.1f°) · 거리 지도 ≤0 칸 %d · 코스트맵 치명 %d' % (lab, rx, ry, math.degrees(ryaw), nocc, nl), fontsize=10, loc='left')
    ax.set_xlabel('map x (m) — 로버는 왼쪽(x 약 0)에서 +x 를 봄')
    if i == 0: ax.set_ylabel('map y (m)')
    # 행별 서쪽 면
    for y0 in np.arange(-0.20, 0.051, 0.05):
        kq = band & (np.abs(P[:, 1] - y0) < 0.025) & (P[:, 0] > 1.0) & (P[:, 0] < 1.4)
        pc = np.percentile(P[kq, 0], 5) if kq.sum() > 30 else np.nan
        ks = (np.abs(S[:, 1] - y0) < 0.026) & (S[:, 2] <= 0); sx = S[ks, 0].min() - R0 / 2 if ks.any() else np.nan
        kl = (np.abs(L[:, 1] - y0) < 0.026) & (L[:, 2] >= 100); lx = L[kl, 0].min() - R0 / 2 if kl.any() else np.nan
        rows_all.append((lab.split(' ·')[0], y0, pc, sx, lx, truth, int(kq.sum())))
from matplotlib.lines import Line2D
fig.legend(handles=[Line2D([], [], marker='o', ls='', color='#6b7680', ms=4), Rectangle((0, 0), 1, 1, fc='#e07b24', alpha=0.75), Rectangle((0, 0), 1, 1, fc='#f6c48f', alpha=0.6),
                    Rectangle((0, 0), 1, 1, fc='none', ec='#c53030', lw=1.8), Line2D([], [], color='#2f855a', lw=2.2), Rectangle((0, 0), 1, 1, fc='none', ec='#2f855a', ls='--')],
           labels=['깊이 점군(높이 0.06~0.30 m)', '거리 지도 ≤ 0 (카메라 점유)', '거리 지도 0~5 cm', '코스트맵 치명 칸', '실제 상자 앞면(줄자)', '기록상 상자 범위(중심 y -0.11 / -0.07)'],
           loc='upper center', ncol=3, fontsize=9, frameon=False, bbox_to_anchor=(0.5, 0.995))
ax = fig.add_subplot(gs[1, :]); ax.axis('off')
hdr = ['조건', '행 y', '점군 앞면(5 %)', '거리 지도 앞면', '코스트맵 앞면', '실제 앞면', '점군-실제', '거리지도-실제', '코스트맵-실제', '점 수']
cells = []
for c, y0, pc, sx, lx, tr, n in rows_all:
    f = lambda v: '—' if np.isnan(v) else '%.3f' % v; g = lambda v: '—' if np.isnan(v) else '%+.1f cm' % (100 * (v - tr))
    cells.append([c, '%+.2f' % y0, f(pc), f(sx), f(lx), '%.3f' % tr, g(pc), g(sx), g(lx), str(n)])
t = ax.table(cellText=cells, colLabels=hdr, loc='upper center', cellLoc='center'); t.auto_set_font_size(False); t.set_fontsize(8.5); t.scale(1, 1.25)
ax.set_title('행(y, 5 cm)마다 상자 서쪽 면 x — 음수 = 실제 면보다 로버 쪽(앞), 양수 = 실제 면보다 뒤(덜 찍음)', fontsize=10, loc='left')
fig.suptitle('시험 상자 정면 0.92 m — nvblox site 거리 2.0 vs 1.0 (정지, 출발 테이프)', fontsize=12, x=0.01, ha='left', y=1.02)
fig.savefig(out, dpi=125, bbox_inches='tight'); print('저장', out)
for r in cells: print(' | '.join(r))
