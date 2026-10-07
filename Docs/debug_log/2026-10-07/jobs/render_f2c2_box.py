# 10-07 §2.5: f2c2 복귀 마지막 구간 — 라이다 점(지도 좌표)으로 상자 위치, 차체 외곽(2 s 마다), 계획 경로, 외곽 ↔ 라이다 최근접 시계열
import numpy as np, math, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
plt.rcParams['font.family'] = 'Malgun Gothic'; plt.rcParams['axes.unicode_minus'] = False
Z = np.load('x912_f2c2.npz'); T0 = 1791338894.0; G6 = T0 + 307.8; LX, LY = 0.152, math.pi - 0.04677; XB, XF, HW = -0.248, 0.262, 0.165
tr = Z['traj']; pt, pn, pxy = Z['plan_t'], Z['plan_n'], Z['plan_xy']; off = np.r_[0, np.cumsum(pn)]
def pose(t): j = np.argmin(np.abs(tr[:, 0] - t)); return tr[j, 1:]
rows = []; allpts = []
for k, t in enumerate(Z['scan_t']):
    if t < G6 + 60: continue
    r = Z['scan_r'][k]; a0, da = Z['scan_a'][k]; a = a0 + da * np.arange(len(r)) + LY; ok = np.isfinite(r) & (r > .05) & (r < 2.5)
    bx, by = LX + r[ok] * np.cos(a[ok]), r[ok] * np.sin(a[ok])
    dx = np.where(bx > XF, bx - XF, np.where(bx < XB, XB - bx, 0)); dy = np.maximum(np.abs(by) - HW, 0); d = np.hypot(dx, dy); j = np.argmin(d)
    x, y, th = pose(t); c, s = math.cos(th), math.sin(th); allpts.append(np.c_[x + c * bx - s * by, y + s * bx + c * by])
    side = ('앞' if bx[j] > XF else '뒤' if bx[j] < XB else '') + ('왼' if by[j] > HW else '오' if by[j] < -HW else '')
    rows.append((t - G6, d[j], side or '안', bx[j], by[j], x, y, math.degrees(th)))
for rw in rows: print('  %+6.1f s  외곽↔라이다 최근접 %.3f m (%s, 차체 %+.2f,%+.2f) | 자세 (%.2f, %.2f, %+4.0f°)' % rw)
P = np.vstack(allpts)
fig, ax = plt.subplots(1, 2, figsize=(15, 6.5), dpi=110, gridspec_kw={'width_ratios': [1.5, 1]})
a = ax[0]; a.scatter(P[:, 0], P[:, 1], s=1, c='#999', label='라이다 점(+60~+120 s, 1 s 마다)')
i = np.flatnonzero(pt >= G6 - 1); 
for k in i: Q = pxy[off[k]:off[k + 1]]; a.plot(Q[:, 0], Q[:, 1], '--', lw=1.2, label='계획 %+.0f s' % (pt[k] - G6))
cm = plt.get_cmap('viridis')
for t in np.arange(G6 + 60, G6 + 121, 2):
    x, y, th = pose(t); c, s = math.cos(th), math.sin(th); C = np.array([[XF, HW], [XF, -HW], [XB, -HW], [XB, HW], [XF, HW]])
    W = np.c_[x + c * C[:, 0] - s * C[:, 1], y + s * C[:, 0] + c * C[:, 1]]; a.plot(W[:, 0], W[:, 1], color=cm((t - G6 - 60) / 60), lw=1)
    a.plot([x, x + .3 * c], [y, y + .3 * s], color=cm((t - G6 - 60) / 60), lw=1.5)
a.plot(0, 0, 'k*', ms=12); a.set_aspect('equal'); a.set_xlim(-0.6, 3.0); a.set_ylim(-1.8, 0.9); a.grid(alpha=.3); a.legend(fontsize=7, loc='lower left')
a.set_title('복귀 마지막 60 s: 차체 외곽(2 s 마다, 보라→노랑 = 시간)·앞쪽 선 = 진행 방향', fontsize=10)
R = np.array([r[:2] for r in rows]); ax[1].plot(R[:, 0], R[:, 1] * 100, '-o', ms=3); ax[1].set_xlabel('목표 6 시작 뒤 s'); ax[1].set_ylabel('차체 외곽 ↔ 라이다 최근접 (cm)'); ax[1].grid(alpha=.3)
ax[1].set_title('라이다로 본 최소 여유', fontsize=10)
fig.tight_layout(); fig.savefig('f2c2_box.png'); print('ok')
