# 10-06 하루 시각화: ① 합성 가림 조건별 EKF B 오차(정적·움직이는 몸) ② 원위치 단계 오차 누적 ③ 회전 중 rf2o 병진 속도 분포(G4 근거) ④ G3 q 분포(기각 근거)
import numpy as np, csv, math, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
plt.rcParams['font.family'] = 'Malgun Gothic'; plt.rcParams['axes.unicode_minus'] = False
FIG = r'F:\6_Indoor_Rover\Rover\Docs\04_navigation\figures\2026-10-06_'
TAPE = [44.8, 10.8, 43.3, 16.1, 43.5, 17.6]
ST = {'0 %': [-3.1, 0.0, -3.3, -0.0, -2.8, 0.2], '16 %': [-3.2, 0.3, -3.4, 0.9, -3.3, 2.1], '32 %': [-3.6, 0.6, -3.9, 2.0, -3.0, 3.6],
      '52 %': [-3.9, 0.5, -3.6, 1.9, -3.2, 3.5], '72 %': [-3.6, -0.7, -1.2, -0.8, -1.9, 0.8]}
MV = {'A 다리 0.8 m': [-3.4, 0.6, -3.3, 0.5, -2.9, 1.9], 'B 다리 0.5 m': [-3.0, 1.0, -3.0, 1.3, -1.9, 2.1],
      'C 50 % 흔듦': [7.6, 3.9, 22.2, 6.5, 15.4, -1.4], 'D 30 % 들락': [-8.5, 11.7, -26.5, 21.6, -40.1, 17.4], 'E 50 % 빠름': [-19.0, 15.0, -4.2, 47.7, 29.6, 51.7]}
fig, ax = plt.subplots(1, 2, figsize=(14, 5), dpi=105)
names = list(ST) + list(MV); vals = [np.mean(np.abs(v)) for v in list(ST.values()) + list(MV.values())]
cols = ['#2f855a'] * 5 + ['#2f855a', '#2f855a', '#c53030', '#c53030', '#c53030']
b = ax[0].bar(range(10), vals, color=cols); ax[0].axhline(3, color='k', ls='--', lw=1); ax[0].text(9.4, 3.6, '판정 3 cm', ha='right', fontsize=8)
ax[0].axvline(4.5, color='#999', lw=1); ax[0].text(2, max(vals) * 0.9, '정지한 몸\n(가린 비율)', ha='center', fontsize=9); ax[0].text(7, max(vals) * 0.9, '움직이는 몸', ha='center', fontsize=9)
ax[0].set_xticks(range(10)); ax[0].set_xticklabels(names, rotation=35, ha='right', fontsize=8); ax[0].set_ylabel('EKF B |예측 - 줄자| 평균 (cm)')
for i, v in enumerate(vals): ax[0].text(i, v + 0.5, '%.1f' % v, ha='center', fontsize=8)
ax[0].set_title('T2 합성: bag_step1 에 사람 몸을 그려 넣고 재생 — 크게 가린 채 움직이면 실패', fontsize=10)
for k, v in list(ST.items())[::2] + list(MV.items()):
    e = [abs(v[i]) for i in (1, 3, 5)]; ax[1].plot([2, 4, 6], e, '-o', lw=1.8, label=k, color=('#2f855a' if k in ST or k.startswith(('A', 'B')) else '#c53030'), alpha=0.5 if k in ST else 1)
ax[1].axhline(3, color='k', ls='--', lw=1); ax[1].set_xticks([2, 4, 6]); ax[1].set_xlabel('원위치 단계 (방향 처음과 같음)'); ax[1].set_ylabel('|EKF B - 줄자| (cm)')
ax[1].set_yscale('symlog', linthresh=3); ax[1].set_yticks([0, 1, 2, 3, 10, 30, 50]); ax[1].set_yticklabels(['0', '1', '2', '3', '10', '30', '50']); ax[1].set_ylim(0, 70); ax[1].legend(fontsize=7, ncol=2); ax[1].grid(alpha=.3)
ax[1].set_title('원위치 단계 오차가 쌓이는가 (초록 = 통과, 빨강 = 실패)', fontsize=10)
fig.tight_layout(); fig.savefig(FIG + 'occ_results.png'); plt.close(fig)
# ③④ 보정 재생 분포
D = {}
for c, lab in (('clean', '깨끗'), ('static50', '정지한 몸 50 %'), ('A_walk08', '다리 걸어 지나감'), ('C_sway', 'C 50 % 흔듦'), ('E_fast', 'E 50 % 빠름')):
    R = list(csv.DictReader(open('qcal/qcal_%s_gate.csv' % c))); A = np.array([[float(r[k]) for k in ('w_gyro', 'bx', 'by', 'q')] for r in R])
    rot = np.abs(A[:, 0]) > 0.15; D[lab] = (np.hypot(A[rot, 1], A[rot, 2]), A[rot, 3][A[rot, 3] >= 0])
fig, ax = plt.subplots(1, 2, figsize=(14, 4.6), dpi=105)
cl = {'깨끗': '#2b6cb0', '정지한 몸 50 %': '#63b3ed', '다리 걸어 지나감': '#2f855a', 'C 50 % 흔듦': '#dd6b20', 'E 50 % 빠름': '#c53030'}
for k, (v, q) in D.items():
    ax[0].plot(np.sort(v), np.linspace(0, 1, len(v)), lw=2, color=cl[k], label=k); ax[1].plot(np.sort(q), np.linspace(0, 1, len(q)), lw=2, color=cl[k], label=k)
for x, l in ((0.05, 'σ 키움 0.05'), (0.10, '버림 0.10')): ax[0].axvline(x, color='k', ls='--', lw=1); ax[0].text(x + 0.005, 0.05, l, fontsize=8)
ax[0].set_xlim(0, 0.4); ax[0].set_xlabel('회전 중 rf2o 병진 속도 |v| (m/s)'); ax[0].set_ylabel('누적 비율'); ax[0].legend(fontsize=8); ax[0].grid(alpha=.3)
ax[0].set_title('G4 근거: 깨끗한 회전의 실제 미끄러짐은 대부분 < 0.05 m/s, 오염은 그 위로 퍼짐', fontsize=10)
ax[1].set_xlim(0, 0.4); ax[1].set_xlabel('G3 q (스캔 겹침 어긋남 비율)'); ax[1].legend(fontsize=8); ax[1].grid(alpha=.3)
ax[1].set_title('G3 기각: 가장 크게 실패한 C 의 q 가 깨끗보다 낮음(느린 움직임은 프레임 간 5 cm 안)', fontsize=10)
fig.tight_layout(); fig.savefig(FIG + 'gate_quality.png'); plt.close(fig); print('ok')
