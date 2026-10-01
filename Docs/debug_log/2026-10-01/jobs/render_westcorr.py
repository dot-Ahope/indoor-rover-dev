# 10-01 §8.31: f2a10 목표 2(서쪽 통로 중간) — 왜 통로를 못 지났나. 같은 시각의 두 판:
#   왼쪽 = 전역 코스트맵(경로 계획이 보는 것): 회색 = 저장 지도만의 비용, 자홍 = 센서가 새로 막은 칸(내접 이상), 빨강 = 라이다, 하늘 = 경로
#   오른쪽 = 로컬 코스트맵(MPPI 가 보는 것): 자홍 ≥ 내접, 연분홍 50~98, 주황 = 카메라(nvblox) 장애물, 빨강 = 라이다
import os, math, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from PIL import Image
from scipy import ndimage
plt.rcParams['font.family'] = 'Malgun Gothic'; plt.rcParams['axes.unicode_minus'] = False
SP = r'C:\Users\magma\AppData\Local\Temp\claude\F--6-Indoor-Rover-Rover\21d4aa9f-8412-4905-b23d-17554af330ea\scratchpad'
G = np.load(SP + r'\f2a6\f2a10_gviz.npz', allow_pickle=True)['recs']; L = np.load(SP + r'\f2a6\f2a10_lviz.npz', allow_pickle=True)['recs']
im = np.array(Image.open(r'F:\6_Indoor_Rover\Rover\Docs\04_navigation\maps\office_v2.pgm')); mr = 0.05; mox, moy = -5.29, -6.96; MH, MW = im.shape
d = ndimage.distance_transform_edt(im != 0) * mr
base = np.where(d <= 0.175, 253, np.where(d <= 0.70, 252 * np.exp(-2.0 * (d - 0.175)), 0)); base[im == 0] = 254
baseO = np.where(base >= 254, 100, np.where(base >= 253, 99, np.where(base <= 0, 0, 1 + 97 * (base - 1) / 251)))
yy, xx = np.mgrid[0:MH, 0:MW]; wx = mox + (xx + 0.5) * mr; wy = moy + (MH - 1 - yy + 0.5) * mr
XL, YL = (-2.6, 0.3), (-6.1, -3.0)
OUT = SP + r'\westviz'; os.makedirs(OUT, exist_ok=True)
FP = np.array([[0.262, 0.165], [0.262, -0.165], [-0.248, -0.165], [-0.248, 0.165], [0.262, 0.165]])
def robot(ax, pose):
    X, Y, TH = pose; c, s = math.cos(TH), math.sin(TH)
    ax.plot(X + c * FP[:, 0] - s * FP[:, 1], Y + s * FP[:, 0] + c * FP[:, 1], '-', color='lime', lw=2.5)
    ax.annotate('', xy=(X + 0.3 * c, Y + 0.3 * s), xytext=(X, Y), arrowprops=dict(arrowstyle='->', color='lime', lw=2))
def common(ax, rec):
    if 'scan' in rec: ax.plot(rec['scan'][:, 0], rec['scan'][:, 1], '.', ms=2.5, color='r', label='라이다(0.185 m 높이)')
    p = rec.get('plan')
    if p is not None and len(p): ax.plot(p[:, 0], p[:, 1], '-', color='#00b7eb', lw=2.2, label='당시 전역 경로')
    robot(ax, rec['pose'])
    ax.add_patch(plt.Circle((-1.64, -4.41), 0.3, fill=False, ec='b', ls='--', lw=1.5)); ax.text(-2.55, -4.3, '서쪽 통로\n병목', color='b', fontsize=9)
    ax.plot(-1.65, -3.7, '*', color='r', ms=15); ax.text(-1.55, -3.62, '목표 2', color='r', fontsize=10, fontweight='bold')
    ax.set_xlim(*XL); ax.set_ylim(*YL); ax.grid(alpha=.25)
n = min(len(G), len(L)); key = []
for k in range(n):
    g, l = G[k], L[k]; t = g['t'] - 5.0
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(15, 7), dpi=85)
    gg = g['gcm'].astype(float); gox, goy, gres = g['gcm_o']; GH, GW = gg.shape
    gi = ((wy - goy) / gres).astype(int); gj = ((wx - gox) / gres).astype(int); ok = (gi >= 0) & (gi < GH) & (gj >= 0) & (gj < GW)
    Gm = np.full((MH, MW), -1.0); Gm[ok] = gg[gi[ok], gj[ok]]; nb = (Gm >= 99) & (baseO < 99)
    bg = np.ones((MH, MW, 3)); bg[..., :] = (1 - baseO[..., None] / 100 * 0.75); bg[im == 0] = 0.1
    a1.imshow(bg, extent=[mox, mox + MW * mr, moy, moy + MH * mr], interpolation='nearest')
    ov = np.zeros((MH, MW, 4)); ov[nb] = (0.85, 0, 0.75, 0.75); a1.imshow(ov, extent=[mox, mox + MW * mr, moy, moy + MH * mr], interpolation='nearest')
    common(a1, g); a1.legend(loc='lower left', fontsize=8); a1.set_title('전역(경로 계획) — 자홍 = 센서가 새로 막은 칸', fontsize=10)
    bg2 = np.ones((MH, MW, 3)) * 0.85; bg2[im == 254] = 1; bg2[im == 0] = 0.2
    a2.imshow(bg2, extent=[mox, mox + MW * mr, moy, moy + MH * mr], interpolation='nearest')
    lc = l['gcm'].astype(float); lox, loy, lres = l['gcm_o']; LH, LW = lc.shape
    rgba = np.zeros((LH, LW, 4)); rgba[lc >= 99] = (0.85, 0, 0.75, 0.8); rgba[(lc >= 50) & (lc < 99)] = (1, 0.6, 0.9, 0.45)
    a2.imshow(rgba, origin='lower', extent=[lox, lox + LW * lres, loy, loy + LH * lres], interpolation='nearest')
    if 'nv' in l:
        nv = l['nv']; nox, noy, nres, unk = l['nv_o']; oi, oj = np.where((nv <= 0.05) & (nv < unk * 0.5))
        a2.plot(nox + (oj + .5) * nres, noy + (oi + .5) * nres, 's', ms=3, color='#ff8c00', label='카메라(nvblox) 장애물')
    common(a2, l); a2.legend(loc='lower left', fontsize=8); a2.set_title('로컬(MPPI) — 자홍 ≥ 내접, 연분홍 50~98', fontsize=10)
    fig.suptitle('f2a10 목표 2(서쪽 통로 중간) 시작 후 %+.0f s' % t, fontsize=12)
    fig.tight_layout(); fig.savefig(OUT + r'\f%03d.png' % k); plt.close(fig); key.append(t)
print('프레임', n, '시각', [round(x) for x in key[::8]])
