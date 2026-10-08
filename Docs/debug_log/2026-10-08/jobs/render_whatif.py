# 10-08 §2: 카메라만 본 장애물 묶음(전역 nvblox 였다면 계획기에 들어갔을 칸)을 저장 지도 위에 번호로 — 사용자가 실제 물체인지 확인
import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
plt.rcParams['font.family'] = 'Malgun Gothic'; plt.rcParams['axes.unicode_minus'] = False
fig, axs = plt.subplots(1, 2, figsize=(16, 7.5), dpi=110)
for ax, n in zip(axs, ('f2c2', 'f2d2')):
    Z = np.load('wi_%s.npz' % n); g = Z['map']; res, ox, oy = Z['meta']
    img = np.where(g < 0, 0.62, np.where(g >= 50, 0.0, 1.0))
    ax.imshow(img, origin='lower', cmap='gray', vmin=0, vmax=1, extent=[ox, ox + g.shape[1] * res, oy, oy + g.shape[0] * res])
    K = Z['keys'] * 0.1; dur = Z['dur']; sc = ax.scatter(K[:, 0], K[:, 1], c=np.minimum(dur, 120), cmap='autumn_r', s=10, marker='s', vmin=0, vmax=120)
    R = Z['rows']; order = np.argsort(-R[:, 0] * R[:, 1])[:15]
    for i, k in enumerate(order):
        cnt, d, fr, cx, cy, w = R[k]; ax.annotate(str(i + 1), (cx, cy), xytext=(cx + 0.35, cy + 0.35), fontsize=10, weight='bold', color='#0050c8', arrowprops=dict(arrowstyle='-', color='#0050c8', lw=0.8))
    ax.set_xlim(-3.2, 7.6); ax.set_ylim(-7.0, 2.2); ax.set_aspect('equal'); ax.grid(alpha=.25)
    ax.set_title('%s: 카메라만 본 장애물(라이다·저장 지도엔 없음) — 색 = 지속 s, 번호 = 큰 묶음 순' % n, fontsize=10)
    for i, k in enumerate(order):
        cnt, d, fr, cx, cy, w = R[k]; ax.text(1.02, 0.98 - i * 0.045, '%2d (%5.2f,%5.2f) %3d칸 %4.0f s' % (i + 1, cx, cy, cnt, d), transform=ax.transAxes, fontsize=7.5, family='Consolas', va='top')
plt.colorbar(sc, ax=axs, shrink=0.6, label='지속(s, 120 이상은 같은 색)')
fig.savefig(r'F:\6_Indoor_Rover\Rover\Docs\04_navigation\figures\2026-10-08_nvblox_global_whatif.png', bbox_inches='tight'); print('ok')
