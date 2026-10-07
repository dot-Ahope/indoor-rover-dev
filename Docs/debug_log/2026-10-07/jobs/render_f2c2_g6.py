# 10-07 §2.5: f2c2 마지막 목표(출발 복귀) — 계획 경로(시각별)와 실제 궤적, 전역 코스트맵 위 상자. 사용자 관찰 "상자를 피하는 경로였는데 다시 상자 쪽으로 틀어 돌아옴" 확인
import numpy as np, math, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
plt.rcParams['font.family'] = 'Malgun Gothic'; plt.rcParams['axes.unicode_minus'] = False
Z = np.load('x912_f2c2.npz'); T0 = 1791338894.0; G6 = T0 + 307.8; G5 = T0 + 176.6
tr = Z['traj']; pt, pn, pxy = Z['plan_t'], Z['plan_n'], Z['plan_xy']; off = np.r_[0, np.cumsum(pn)]
print('계획 경로 시각(목표 기준 s)·점 수·끝:'); 
for i, t in enumerate(pt): P = pxy[off[i]:off[i + 1]]; print('  %+7.1f s (목표%s) 점 %d 시작 (%.2f,%.2f) 끝 (%.2f,%.2f)' % (t - G6, '6' if t >= G6 else '5', len(P), *P[0], *P[-1]))
fig, ax = plt.subplots(1, 2, figsize=(15, 7), dpi=110)
for k, (a, lo, hi, title) in enumerate(((ax[0], G6, G6 + 125, '목표 6: W3 (5.5, −2.2) → 출발 (0, 0)'), (ax[1], G6 + 60, G6 + 125, '확대: 출발 방 마지막 65 s'))):
    gi = np.argmin(np.abs(Z['gcm_t'] - (G6 + 90))); g = Z['gcm'][gi].astype(float); res, ox, oy = Z['gcm_meta'][gi]
    g[g < 0] = np.nan; a.imshow(g, origin='lower', extent=[ox, ox + g.shape[1] * res, oy, oy + g.shape[0] * res], cmap='Greys', vmin=0, vmax=100, alpha=.8)
    sel = (tr[:, 0] >= lo) & (tr[:, 0] <= hi); sc = a.scatter(tr[sel, 1], tr[sel, 2], c=tr[sel, 0] - G6, cmap='viridis', s=6, zorder=3)
    for i, t in enumerate(pt):
        if t >= G6 - 1:
            P = pxy[off[i]:off[i + 1]]; a.plot(P[:, 0], P[:, 1], '--', lw=1.4, zorder=2, label='계획 %+.0f s' % (t - G6))
    for t in np.arange(lo, hi, 5):   # 5 s 마다 차체 방향 화살표
        j = np.argmin(np.abs(tr[:, 0] - t)); x, y, th = tr[j, 1:]; a.annotate('', (x + .25 * math.cos(th), y + .25 * math.sin(th)), (x, y), arrowprops=dict(arrowstyle='->', color='crimson', lw=1.2), zorder=4)
    a.plot(0, 0, 'k*', ms=14, zorder=5); a.set_aspect('equal'); a.set_title(title, fontsize=10); a.grid(alpha=.3)
    xs, ys = tr[sel, 1], tr[sel, 2]; pad = .6; a.set_xlim(min(xs.min(), 0) - pad, max(xs.max(), 0) + pad); a.set_ylim(min(ys.min(), 0) - pad, max(ys.max(), 0) + pad)
    plt.colorbar(sc, ax=a, label='목표 6 시작 뒤 s', shrink=.7); a.legend(fontsize=7, loc='best')
fig.suptitle('f2c2 마지막 복귀 — 전역 코스트맵(+90 s 시점, 짙을수록 비용 큼) 위 계획 경로(점선)·실제 궤적(점, 시간색)·5 s 마다 차체 방향(빨간 화살표)', fontsize=10)
fig.tight_layout(); fig.savefig('f2c2_g6.png'); print('ok')
