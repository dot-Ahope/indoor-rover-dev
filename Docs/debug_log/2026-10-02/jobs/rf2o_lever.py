# 10-02 §18: rf2o 단독 자세의 출렁임이 실제 차체 움직임인지, 라이다 위치(중심 앞 0.152 m)의 원운동인지 확인
#   rf2o 자세(부호 보정)에서 라이다 지렛대를 빼 차체 중심을 구해 EKF B 와 비교, 오른쪽 앞끝 궤적도 같이
import numpy as np, math, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
plt.rcParams['font.family'] = 'Malgun Gothic'; plt.rcParams['axes.unicode_minus'] = False
def srt(a): return a[np.argsort(a[:, 0])]
Z = np.load('f2a6/r2_rot3.npz'); B, OB = srt(Z['B']), srt(Z['ob']); R = srt(np.load('f2a6/rf2o_rot3.npz')['rf'])
t0, t1 = B[0, 0] + 0.5, B[-1, 0] - 0.5; R = R[(R[:, 0] >= t0) & (R[:, 0] <= t1)]; B = B[(B[:, 0] >= t0) & (B[:, 0] <= t1)]
def inframe(x, y, x0, y0, th0):
    c, s = math.cos(th0), math.sin(th0); dx, dy = x - x0, y - y0; return c * dx + s * dy, -s * dx + c * dy
# rf2o 원 자세: 부호 반전(라이다 뒤집힘)한 것이 '라이다 위치' 라고 가정 → 중심 = 라이다 − R(yaw)·(0.152, 0)
rx, ry = inframe(R[:, 1], R[:, 2], R[0, 1], R[0, 2], R[0, 3]); rx, ry = -rx, -ry
yaw = R[:, 3] - R[0, 3]
cx, cy = rx - 0.152 * np.cos(yaw) + 0.152, ry - 0.152 * np.sin(yaw)
bx, by = inframe(B[:, 1], B[:, 2], B[0, 1], B[0, 2], B[0, 3]); byaw = B[:, 3] - B[0, 3]
def corner(x, y, th): return x + 0.262 * np.cos(th) + 0.165 * np.sin(th) - 0.262, y + 0.262 * np.sin(th) - 0.165 * np.cos(th) + 0.165
fig, ax = plt.subplots(1, 2, figsize=(13, 6), dpi=105)
ax[0].plot(rx, ry, ':', color='#805ad5', lw=1.4, label='rf2o 원 자세(부호 보정)')
ax[0].plot(cx, cy, '-', color='#805ad5', lw=2, label='rf2o − 라이다 지렛대 0.152 m = 차체 중심')
ax[0].plot(bx, by, '-', color='#2f855a', lw=2, label='EKF B 차체 중심')
ax[0].plot(-0.275, -0.245, 'X', color='k', ms=12, label='줄자 끝(오른쪽 앞끝 이동 = 중심 이동, 방향 원위치)')
ax[0].set_aspect('equal'); ax[0].grid(alpha=.3); ax[0].legend(fontsize=8, loc='upper left'); ax[0].set_title('차체 중심: 출렁임이 라이다 지렛대 몫인지', fontsize=10)
for (x, y, th, col, lab) in ((cx, cy, yaw, '#805ad5', 'rf2o(중심 환산)'), (bx, by, byaw, '#2f855a', 'EKF B')):
    kx, ky = corner(x, y, th); ax[1].plot(kx, ky, '-', color=col, lw=1.8, label=lab + ' — 오른쪽 앞끝')
ax[1].plot(0, 0, 's', color='k'); ax[1].plot(-0.275, -0.245, 'X', color='k', ms=12, label='줄자 끝')
ax[1].set_aspect('equal'); ax[1].grid(alpha=.3); ax[1].legend(fontsize=8, loc='upper left'); ax[1].set_title('오른쪽 앞끝(줄자 재는 점)의 궤적 — 회전만으로도 크게 움직임', fontsize=10)
for a in ax: a.set_xlabel('시작 자세 기준 앞(+) m'); a.set_ylabel('왼(+) m')
fig.tight_layout(); fig.savefig(r'F:\6_Indoor_Rover\Rover\Docs\04_navigation\figures\2026-10-02_rf2o_lever.png')
print('rf2o 원 자세 경로 %.2f m · 중심 환산 %.2f m · EKF B %.2f m | 끝 중심 환산 (%.3f, %.3f), EKF B (%.3f, %.3f)' % (np.sum(np.hypot(np.diff(rx), np.diff(ry))), np.sum(np.hypot(np.diff(cx), np.diff(cy))), np.sum(np.hypot(np.diff(bx), np.diff(by))), cx[-1], cy[-1], bx[-1], by[-1]))
