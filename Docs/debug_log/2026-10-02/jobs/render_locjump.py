# 10-02 §2: f2a12 위치 추정 재생 — map→odom x 시계열(라이브 기록 vs 재생 3 조합)
import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
plt.rcParams['font.family'] = 'Malgun Gothic'; plt.rcParams['axes.unicode_minus'] = False
SP = r'C:\Users\magma\AppData\Local\Temp\claude\F--6-Indoor-Rover-Rover\21d4aa9f-8412-4905-b23d-17554af330ea\scratchpad\f2a6'
A = np.load(SP + r'\locjump_office_v2_3.0.npz'); B = np.load(SP + r'\locjump_cand_1002_f2a12_c276_nolc_3.0.npz'); C = np.load(SP + r'\locjump_office_v2_1.0.npz')
fig, ax = plt.subplots(figsize=(10, 4.4), dpi=110)
L = A['live']; ax.plot(L[:, 0], L[:, 1], '-', color='#999', lw=5, alpha=.6, label='라이브 기록 (f2a12)')
for D, c, lab in ((A, '#c53030', '재생: office_v2 · 탐색 창 3.0 (기준선)'), (B, '#2f855a', '재생: 보완 지도 후보 · 3.0'), (C, '#2b6cb0', '재생: office_v2 · 탐색 창 1.0')):
    R = D['rep']; ax.plot(R[:, 0], R[:, 1], '-', color=c, lw=1.6, label=lab)
ax.axvline(283.0, color='#c05621', ls='--', lw=1); ax.text(284.5, -0.9, '라이브 점프\n+283.0 s', color='#c05621', fontsize=9)
ax.set_xlabel('bag 시각 (s)'); ax.set_ylabel('map→odom x (m)'); ax.set_xlim(0, 345); ax.grid(alpha=.3); ax.legend(loc='lower left', fontsize=8)
ax.set_title('f2a12 bag 위치 추정 재생: 기준선은 점프를 그대로 재현(+281.9 s, 1.28 m), 지도 보완·탐색 창 축소는 둘 다 점프 없음', fontsize=10)
fig.tight_layout(); fig.savefig(r'F:\6_Indoor_Rover\Rover\Docs\04_navigation\figures\2026-10-02_locjump_replay.png'); print('ok')
