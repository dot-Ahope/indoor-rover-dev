# 10-02 §9: f2b4 출발 방 복귀 — 상자를 봤나(로컬 코스트맵·nvblox·라이다·전역, 6 장면)
import math, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from PIL import Image
plt.rcParams['font.family'] = 'Malgun Gothic'; plt.rcParams['axes.unicode_minus'] = False
SP = r'C:\Users\magma\AppData\Local\Temp\claude\F--6-Indoor-Rover-Rover\21d4aa9f-8412-4905-b23d-17554af330ea\scratchpad'
L = np.load(SP + r'\f2a6\f2b4_lviz.npz', allow_pickle=True)['recs']; G = np.load(SP + r'\f2a6\f2b4_gviz.npz', allow_pickle=True)['recs']
im = np.array(Image.open(r'F:\6_Indoor_Rover\Rover\Docs\04_navigation\maps\office_v3.pgm')); H, W = im.shape
bg = np.where(im == 0, 0.15, np.where(im == 254, 1.0, 0.85)); E = [-5.29, -5.29 + W * .05, -6.96, -6.96 + H * .05]
FP = np.array([[0.262, 0.165], [0.262, -0.165], [-0.248, -0.165], [-0.248, 0.165], [0.262, 0.165]])
fig, axs = plt.subplots(2, 3, figsize=(16, 10.5), dpi=90)
for ax, w in zip(axs.ravel(), (44, 50, 56, 60, 63, 66)):
    k = int(np.argmin([abs(r['t'] - w) for r in L])); r, g = L[k], G[k]
    X, Y, T = r['pose']; tx, ty, tw = r['mo']; cc, ss = math.cos(tw), math.sin(tw)
    ax.imshow(bg, cmap='gray', vmin=0, vmax=1, extent=E, interpolation='nearest')
    gg = g['gcm']; gox, goy, gres = g['gcm_o']; ii, jj = np.where(gg >= 99)
    ax.scatter(gox + (jj + .5) * gres, goy + (ii + .5) * gres, s=55, marker='s', facecolor='none', edgecolor='#2b6cb0', lw=.8, label='전역 ≥ 내접')
    lc = r['gcm']; ox, oy, res = r['gcm_o']; ii, jj = np.where(lc >= 99); lx, ly = ox + (jj + .5) * res, oy + (ii + .5) * res
    ax.scatter(tx + cc * lx - ss * ly, ty + ss * lx + cc * ly, s=30, marker='s', color=(0.85, 0, 0.7, .5), lw=0, label='로컬 ≥ 내접')
    nv = r['nv']; nox, noy, nres, unk = r['nv_o']; ii, jj = np.where((nv <= 0.05) & (nv < unk * .5)); vx, vy = nox + (jj + .5) * nres, noy + (ii + .5) * nres
    ax.plot(tx + cc * vx - ss * vy, ty + ss * vx + cc * vy, 's', ms=3, color='#ff8c00', label='nvblox 장애')
    ax.plot(r['scan'][:, 0], r['scan'][:, 1], '.', ms=3, color='r', label='라이다')
    p = g.get('plan')
    if p is not None and len(p): ax.plot(p[:, 0], p[:, 1], '-', color='#00b7eb', lw=2, label='경로')
    c, s = math.cos(T), math.sin(T); ax.plot(X + c * FP[:, 0] - s * FP[:, 1], Y + s * FP[:, 0] + c * FP[:, 1], '-', color='lime', lw=2.5, label='로버')
    ax.add_patch(plt.Rectangle((1.15, -0.17), 0.10, 0.17, fill=False, ec='k', ls='--', lw=1.5)); ax.text(1.15, -0.30, '상자 자리(10-01)', fontsize=8)
    ax.set_xlim(X - 1.2, X + 1.2); ax.set_ylim(Y - 1.2, Y + 1.2); ax.set_aspect('equal'); ax.grid(alpha=.3)
    ax.set_title('13:50:40 +%.0f s  로버 (%.2f, %.2f, %.0f°)' % (r['t'], X, Y, math.degrees(T)), fontsize=10)
axs[0, 0].legend(loc='lower left', fontsize=7, framealpha=.9)
fig.suptitle('f2b4 출발 방 복귀 — 상자 자리(점선)에 전역·로컬·nvblox 표시가 있었나', fontsize=12)
fig.tight_layout(); fig.savefig(r'F:\6_Indoor_Rover\Rover\Docs\04_navigation\figures\2026-10-02_f2b4_box.png'); print('ok')
