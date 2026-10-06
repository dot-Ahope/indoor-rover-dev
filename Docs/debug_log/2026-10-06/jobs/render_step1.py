# 10-06 §4: 단계별 회전 실측 결과 — 각 단계에서 오른쪽 앞끝의 예측 위치(EKF B·A·SLAM)와 줄자 대각 거리(원)
import json, math, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
plt.rcParams['font.family'] = 'Malgun Gothic'; plt.rcParams['axes.unicode_minus'] = False
S = json.load(open('step1/step_state_1.json')); TAPE = [44.8, 10.8, 43.3, 16.1, 43.5, 17.6]
C = {'B': '#2f855a', 'A': '#c05621', 'S': '#2b6cb0'}; NM = {'B': 'EKF B (rf2o 보정)', 'A': 'EKF A (지금)', 'S': 'SLAM'}
CR = np.array([0.262, -0.165])
def rel(p, p0):
    c0, s0 = math.cos(p0[2]), math.sin(p0[2]); dx, dy = p[0] - p0[0], p[1] - p0[1]; return [c0 * dx + s0 * dy, -s0 * dx + c0 * dy, p[2] - p0[2]]
def corner(p): c, s = math.cos(p[2]), math.sin(p[2]); return np.array([p[0] + c * CR[0] - s * CR[1], p[1] + s * CR[0] + c * CR[1]]) - CR
pred = {k: [] for k in 'BAS'}; pts = {k: [] for k in 'BAS'}
for st in S['steps']:
    for k in 'BAS':
        d = corner(rel(st['pose'][k], S['s0'][k])); pts[k].append(d); pred[k].append(np.hypot(*d) * 100)
err = {k: np.array(pred[k]) - np.array(TAPE) for k in 'BAS'}
fig, ax = plt.subplots(1, 2, figsize=(14, 5.8), dpi=105)
x = np.arange(1, 7); w = 0.26
for i, k in enumerate('BAS'):
    ax[0].bar(x + (i - 1) * w, err[k], w, color=C[k], label='%s — |오차| 평균 %.1f cm' % (NM[k], np.abs(err[k]).mean()))
ax[0].axhline(0, color='k', lw=.8); ax[0].axhspan(-3, 3, color='#e6f2ea', zorder=0)
ax[0].set_xticks(x); ax[0].set_xticklabels(['%d\n%s\n줄자 %.1f' % (i + 1, s['dir'], TAPE[i]) for i, s in enumerate(S['steps'])], fontsize=8)
ax[0].set_ylabel('예측 대각 거리 - 줄자 (cm)'); ax[0].legend(fontsize=8, loc='lower left'); ax[0].grid(alpha=.3, axis='y')
ax[0].set_title('단계별 오차 (초록 띠 = ±3 cm 판정 기준). 짝수 단계 = 방향 원위치, 줄자 = 순수 미끄러짐', fontsize=9.5)
# 짝수 단계: 방향 원위치 → 오른쪽 앞끝 이동 = 중심 미끄러짐. 줄자 원 + 사용자 방향(뒤·오른쪽)
for j, i in enumerate((1, 3, 5)):
    ax[1].add_patch(plt.Circle((0, 0), TAPE[i] / 100, fill=False, ec='#888', ls='--', lw=1))
    r = TAPE[i] / 100; a = math.radians(-75); ax[1].text(r * math.cos(a), r * math.sin(a), ' 단계 %d 줄자 %.1f' % (i + 1, TAPE[i]), fontsize=7.5, color='#555', clip_on=True)
for k in 'BAS':
    P = np.array([pts[k][i] for i in (1, 3, 5)]); ax[1].plot(P[:, 0], P[:, 1], '-o', color=C[k], ms=7, label=NM[k])
    for (px, py), i in zip(P, (2, 4, 6)): ax[1].text(px + 0.004, py + 0.004, str(i), fontsize=8, color=C[k])
ax[1].plot(0, 0, 's', color='k'); ax[1].text(0.004, 0.006, '시작 표시', fontsize=8)
ax[1].set_aspect('equal'); ax[1].set_xlim(-0.22, 0.05); ax[1].set_ylim(-0.2, 0.05); ax[1].grid(alpha=.3); ax[1].legend(fontsize=8, loc='upper left')
ax[1].set_xlabel('시작 자세 기준 앞(+) m'); ax[1].set_ylabel('왼(+) m')
ax[1].set_title('방향 원위치 단계(2·4·6)의 오른쪽 앞끝 예측 위치 vs 줄자 거리(점선 원). 사용자 관찰 방향: 뒤·오른쪽', fontsize=9.5)
fig.suptitle('10-06 단계별 회전 실측: 제자리 ±90° × 3, 매 단계 오른쪽 앞끝 대각 거리를 줄자로', fontsize=12)
fig.tight_layout(); fig.savefig(r'F:\6_Indoor_Rover\Rover\Docs\04_navigation\figures\2026-10-06_step_rot1.png')
for k in 'BAS': print(NM[k], ' '.join('%+.1f' % e for e in err[k]), '| 평균 |오차| %.1f' % np.abs(err[k]).mean())
