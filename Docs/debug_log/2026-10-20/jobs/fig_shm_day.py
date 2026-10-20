#!/usr/bin/env python3
"""fig_shm_day — 10-20 §7.5 · §9.3 · §9.5 수치(출력 원문에서 옮김)를 한 그림으로. 인자: 출력.png"""
import sys, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
plt.rcParams['font.family'] = 'Malgun Gothic'; plt.rcParams['axes.unicode_minus'] = False
fig, ax = plt.subplots(1, 3, figsize=(15, 4.6))
# (a) §7.5 UDP 크기별 — 줄마다 두 반복의 평균 Hz(두 줄은 두 줄 평균)
lab = ['38 kB\n(지금 깊이)', '307 kB ×1', '307 kB ×2\n(IR 좌우)', '614 kB\n(깊이 원본)']
r1 = [15.0, 14.8, (14.8 + 14.2) / 2, 14.1]; r2 = [15.0, 14.8, (14.2 + 12.8) / 2, 13.3]
x = range(4); ax[0].bar([i - 0.18 for i in x], r1, 0.34, color='#5b6470', label='반복 1'); ax[0].bar([i + 0.18 for i in x], r2, 0.34, color='#9aa4b0', label='반복 2')
ax[0].axhline(15, color='#1f7a72', lw=1, ls='--'); ax[0].set_ylim(12, 15.4); ax[0].set_xticks(list(x)); ax[0].set_xticklabels(lab, fontsize=9)
ax[0].set_ylabel('컨테이너 수신 Hz (발행 15 Hz)'); ax[0].set_title('(a) UDP: 메시지가 클수록 빠짐 (§7.5)'); ax[0].legend(fontsize=8, loc='lower left')
# (b) §9.3 정지 A/B
c = ['UDP 1', 'SHM', 'UDP 2']; hz = [13.2, 15.0, 13.0]; gap = [101, 1, 115]; col = ['#b3263e', '#1f7a72', '#b3263e']
ax[1].bar(c, hz, color=col); ax[1].set_ylim(12, 15.4); ax[1].set_ylabel('cuVSLAM 출력 Hz')
for i, (h, g) in enumerate(zip(hz, gap)): ax[1].text(i, h + 0.05, '%.1f Hz\n간격 경고 %d' % (h, g), ha='center', fontsize=9)
ax[1].set_title('(b) 카메라→cuVSLAM 공유메모리, 정지 (§9.3)')
# (c) §9.5 재기동 10 회
cyc = list(range(1, 11)); out = [149, 150, 150, 150, 150, 150, 150, 150, 149, 149]
ax[2].plot(cyc, [o / 10 for o in out], 'o-', color='#1f7a72'); ax[2].set_ylim(12, 15.4); ax[2].set_xticks(cyc)
for k, t in {3: '카메라 -9', 6: '카메라 -9', 9: '카메라 -9', 4: 'nvblox -9', 8: 'nvblox -9', 7: 'cuVSLAM -9'}.items():
    ax[2].annotate(t, (k, out[k - 1] / 10), xytext=(k, 13.0 + (0.35 if k % 2 else 0)), ha='center', fontsize=8, arrowprops=dict(arrowstyle='-', color='#a86a00'), color='#a86a00')
ax[2].set_xlabel('prep 회차 (사고 모사는 측정 뒤 → 다음 회 복귀)'); ax[2].set_ylabel('/vslam/odom Hz'); ax[2].set_title('(c) 실제 스택 재기동 10/10 (§9.5)')
for a in ax: a.grid(alpha=0.3, axis='y')
fig.tight_layout(); fig.savefig(sys.argv[1], dpi=105); print('그림', sys.argv[1])
