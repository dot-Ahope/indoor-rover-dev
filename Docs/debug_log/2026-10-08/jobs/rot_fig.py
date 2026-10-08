# 10-08 §4 그림: 회전축 위치(차체 좌표)와 90°당 미끄러짐, 회전 종류별
import numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
plt.rcParams['font.family'] = 'Malgun Gothic'; plt.rcParams['axes.unicode_minus'] = False
A = np.load('rot2_large.npy'); A = A[A[:, 8] == 0]
col = {0: '#c0392b', 1: '#7d3c98', 2: '#2471a3'}; nm = {0: '제자리(두 트랙 반대, 둘 다 ≥0.035 m/s)', 1: '중간(느린 트랙 0.02~0.035 m/s)', 2: '피벗형(느린 트랙 ≤0.02 m/s)'}
fig, (a1, a2) = plt.subplots(1, 2, figsize=(13, 6.2), gridspec_kw={'width_ratios': [1.25, 1]})
for y in (0.1225, -0.1225): a1.add_patch(Rectangle((-14.5, y * 100 - 2.5), 29, 5, fc='#d5d8dc', ec='#7f8c8d'))
a1.plot([-25, 25], [0, 0], c='#bbb', lw=.8); a1.plot([0, 0], [-30, 30], c='#bbb', lw=.8)
a1.annotate('', xy=(22, -27), xytext=(12, -27), arrowprops=dict(arrowstyle='->', color='#555')); a1.text(12, -25.5, '전방', color='#555')
a1.text(-14.5, 15.5, '왼쪽 트랙(중심선 +12.25 cm)', fontsize=9, color='#555'); a1.text(-14.5, -17.5, '오른쪽 트랙', fontsize=9, color='#555')
for k in (0, 1, 2):
    m = A[:, 7] == k; a1.scatter(A[m, 3] * 100, A[m, 4] * 100, s=40 + A[m, 6] * 100 * 25, c=col[k], alpha=.7, ec='w', label=nm[k])
w = A[A[:, 9] == 1]; a1.scatter(w[:, 3] * 100, w[:, 4] * 100, s=260, fc='none', ec='k', lw=1.6, label='f2e2 W3 후진 회전(가장 적게 미끄러짐)')
a1.axvline(np.median(A[:, 3]) * 100, c='#e67e22', ls='--', lw=1.2); a1.text(np.median(A[:, 3]) * 100 - 1, 27, '회전축 앞뒤 중앙 %.1f cm' % (np.median(A[:, 3]) * 100), color='#e67e22', ha='right', fontsize=9)
a1.set_xlim(-25, 25); a1.set_ylim(-30, 30); a1.set_aspect('equal'); a1.set_xlabel('앞(+) / 뒤(-) [cm]  — 0 = base_link(트랙 길이 중점)'); a1.set_ylabel('왼(+) / 오른(-) [cm]')
a1.set_title('회전축(순간 정지점 중앙값) 위치 — 점 크기 = 90°당 미끄러짐', fontsize=11); a1.legend(fontsize=8, loc='lower left')
for i, k in enumerate((0, 1, 2)):
    m = A[:, 7] == k; v = A[m, 6] * 100; x = i + (np.random.default_rng(1).random(m.sum()) - .5) * .25
    a2.scatter(x, v, c=col[k], s=45, alpha=.75, ec='w'); a2.plot([i - .25, i + .25], [np.median(v)] * 2, c=col[k], lw=2.5)
    a2.text(i + .28, np.median(v), '중앙 %.1f\nn=%d' % (np.median(v), m.sum()), va='center', fontsize=9)
    ww = m & (A[:, 9] == 1)
    if ww.any(): a2.scatter(x[ww[m]], A[ww, 6] * 100, s=200, fc='none', ec='k', lw=1.6)
a2.axhspan(5, 13.5, color='#f5b7b1', alpha=.35); a2.text(2.45, 13.2, '09-28 지령 v=0 제자리\n180°당 10~27 cm(=90°당 5~13.5)', fontsize=8, ha='right', va='top')
a2.set_xticks([0, 1, 2], ['제자리', '중간', '피벗형']); a2.set_xlim(-.5, 2.6); a2.set_ylabel('90°당 미끄러짐 [cm]  (스캔 정합 이동 - 휠 추측항법)')
a2.set_title('회전 종류별 미끄러짐 (≥45° 회전 22 개, 10-07·10-08 bag 6 개)', fontsize=11)
fig.tight_layout(); fig.savefig('F:/6_Indoor_Rover/Rover/Docs/04_navigation/figures/2026-10-08_turn_slip_icr.png', dpi=130)
