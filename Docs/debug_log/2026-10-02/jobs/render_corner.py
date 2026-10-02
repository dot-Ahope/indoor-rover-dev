# 10-02 §7: f2b3 남서 구석 정체 — 4 장면(로컬 코스트맵(odom→map 변환)·라이다·차체·경로)
import math, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from PIL import Image
plt.rcParams['font.family'] = 'Malgun Gothic'; plt.rcParams['axes.unicode_minus'] = False
SP = r'C:\Users\magma\AppData\Local\Temp\claude\F--6-Indoor-Rover-Rover\21d4aa9f-8412-4905-b23d-17554af330ea\scratchpad'
L = np.load(SP + r'\f2a6\f2b3_lviz.npz', allow_pickle=True)['recs']
im = np.array(Image.open(r'F:\6_Indoor_Rover\Rover\Docs\04_navigation\maps\office_v3.pgm')); H, W = im.shape
bg = np.where(im == 0, 0.15, np.where(im == 254, 1.0, 0.85)); E = [-5.29, -5.29 + W * .05, -6.96, -6.96 + H * .05]
FP = np.array([[0.262, 0.165], [0.262, -0.165], [-0.248, -0.165], [-0.248, 0.165], [0.262, 0.165]])
want = [27, 30, 33, 36, 42, 48]; idx = [int(np.argmin([abs(r['t'] - w) for r in L])) for w in want]
fig, axs = plt.subplots(2, 3, figsize=(16, 10.5), dpi=90)
for ax, k in zip(axs.ravel(), idx):
    r = L[k]; X, Y, T = r['pose']; tx, ty, tw = r['mo']; cc, ss = math.cos(tw), math.sin(tw)
    ax.imshow(bg, cmap='gray', vmin=0, vmax=1, extent=E, interpolation='nearest')
    g = r['gcm'].astype(float); ox, oy, res = r['gcm_o']
    for th, hi, col, lab in ((100, 101, (0.75, 0, 0.6, .9), '로컬 치명'), (99, 100, (0.95, 0.4, 0.85, .6), '로컬 내접')):
        ii, jj = np.where((g >= th) & (g < hi)); lx, ly = ox + (jj + .5) * res, oy + (ii + .5) * res
        ax.scatter(tx + cc * lx - ss * ly, ty + ss * lx + cc * ly, s=40, marker='s', color=col, lw=0, label=lab)
    ax.plot(r['scan'][:, 0], r['scan'][:, 1], '.', ms=3, color='r', label='라이다')
    p = r.get('plan')
    if p is not None and len(p): ax.plot(p[:, 0], p[:, 1], '-', color='#00b7eb', lw=2, label='경로')
    c, s = math.cos(T), math.sin(T); ax.plot(X + c * FP[:, 0] - s * FP[:, 1], Y + s * FP[:, 0] + c * FP[:, 1], '-', color='lime', lw=2.5, label='로버')
    ax.annotate('', xy=(X + .3 * c, Y + .3 * s), xytext=(X, Y), arrowprops=dict(arrowstyle='->', color='lime', lw=2))
    ax.plot(-1.6, -5.5, '*', color='orange', ms=16, mec='k', label='목표 (149°)')
    ax.set_xlim(X - 0.9, X + 0.9); ax.set_ylim(Y - 0.9, Y + 0.9); ax.set_aspect('equal'); ax.grid(alpha=.3)
    ax.set_title('13:25:30 +%.0f s  로버 (%.2f, %.2f, %.0f°)' % (r['t'], X, Y, math.degrees(T)), fontsize=10)
axs[0, 0].legend(loc='lower left', fontsize=7, framealpha=.9)
fig.suptitle('f2b3 목표 6(D → 남서) — 목표 앞 의자(라이다 점 덩어리)에 붙어 회전하다 정체', fontsize=12)
fig.tight_layout(); fig.savefig(r'F:\6_Indoor_Rover\Rover\Docs\04_navigation\figures\2026-10-02_f2b3_corner.png'); print('ok')
