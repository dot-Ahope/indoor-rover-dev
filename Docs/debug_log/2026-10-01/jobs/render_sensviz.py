# 10-01 §8.22: f2a8 D 구간 — 센서가 통로를 어떻게 '막힘'으로 만들었나(1 s 프레임 → mp4 + 핵심 장면 그림)
#   배경 = 저장 지도(office_v2)만으로 계산한 전역 비용(Nav2 식, 0.70 m·k 2.0) — "센서가 없을 때"
#   자홍 = 기록된 전역 코스트맵에서 내접(무효) 이상인데 저장 지도만으로는 아닌 칸 = **센서가 새로 막은 칸**
#   빨강 점 = 라이다, 주황 = nvblox(카메라) 장애물 칸(거리 ≤ 0.05 m), 하늘 = 당시 경로, 노랑 × = 경로 위 무효 칸
import os, sys, math, subprocess, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from PIL import Image
from scipy import ndimage
plt.rcParams['font.family'] = 'Malgun Gothic'; plt.rcParams['axes.unicode_minus'] = False
ROOT = r'F:\6_Indoor_Rover\Rover'; SP = r'C:\Users\magma\AppData\Local\Temp\claude\F--6-Indoor-Rover-Rover\21d4aa9f-8412-4905-b23d-17554af330ea\scratchpad'
R = np.load(SP + r'\f2a6\f2a8_viz.npz', allow_pickle=True)['recs']
im = np.array(Image.open(ROOT + r'\Docs\04_navigation\maps\office_v2.pgm')); mr = 0.05; mox, moy = -5.29, -6.96; MH, MW = im.shape
d = ndimage.distance_transform_edt(im != 0) * mr
base = np.where(d <= 0.175, 253, np.where(d <= 0.70, 252 * np.exp(-2.0 * (d - 0.175)), 0)); base[im == 0] = 254
def tr(c): return np.where(c >= 254, 100, np.where(c >= 253, 99, np.where(c <= 0, 0, 1 + 97 * (c - 1) / 251)))
baseO = tr(base)   # 저장 지도 행 0 = 위(y 큼)
XL, YL = (-2.5, 4.3), (-6.1, -1.2)
OUT = SP + r'\sensviz'; os.makedirs(OUT, exist_ok=True)
def classify(p):
    if p is None or not len(p): return '?'
    b = p[(p[:, 1] < -3.0) & (p[:, 1] > -4.5)]
    return '?' if not len(b) else ('서' if b[:, 0].mean() < -0.9 else '가운데' if b[:, 0].mean() < 1.6 else '동')
stats = []
for k, rec in enumerate(R):
    g = rec['gcm'].astype(float); gox, goy, gres = rec['gcm_o']; GH, GW = g.shape
    # 기록 코스트맵(행 0 = 아래) → 저장 지도 격자(행 0 = 위)로 맞춤(같은 원점·해상도 가정, 다르면 최근접)
    yy, xx = np.mgrid[0:MH, 0:MW]; wx = mox + (xx + 0.5) * mr; wy = moy + (MH - 1 - yy + 0.5) * mr
    gi = ((wy - goy) / gres).astype(int); gj = ((wx - gox) / gres).astype(int); ok = (gi >= 0) & (gi < GH) & (gj >= 0) & (gj < GW)
    G = np.full((MH, MW), -1.0); G[ok] = g[gi[ok], gj[ok]]
    new_block = (G >= 99) & (baseO < 99)
    fig, ax = plt.subplots(figsize=(12, 8.2), dpi=90)
    bg = np.ones((MH, MW, 3)); bg[..., :] = (1 - baseO[..., None] / 100 * 0.75); bg[im == 0] = 0.1
    ax.imshow(bg, extent=[mox, mox + MW * mr, moy, moy + MH * mr], interpolation='nearest')
    ov = np.zeros((MH, MW, 4)); ov[new_block] = (0.85, 0.0, 0.75, 0.75)
    ax.imshow(ov, extent=[mox, mox + MW * mr, moy, moy + MH * mr], interpolation='nearest')
    if 'nv' in rec:
        nv = rec['nv']; nox, noy, nres, unk = rec['nv_o']; oi, oj = np.where((nv <= 0.05) & (nv < unk * 0.5))
        ax.plot(nox + (oj + 0.5) * nres, noy + (oi + 0.5) * nres, 's', ms=2.2, color='#ff8c00', alpha=.8, label='카메라(nvblox) 장애물')
    if 'scan' in rec: ax.plot(rec['scan'][:, 0], rec['scan'][:, 1], '.', ms=2, color='r', label='라이다')
    p = rec.get('plan'); bad = 0
    if p is not None and len(p):
        ax.plot(p[:, 0], p[:, 1], '-', color='#00b7eb', lw=2.2, label='당시 경로(%s)' % classify(p))
        pi = MH - 1 - ((p[:, 1] - moy) / mr).astype(int); pj = ((p[:, 0] - mox) / mr).astype(int); okp = (pi >= 0) & (pi < MH) & (pj >= 0) & (pj < MW)
        inv = np.zeros(len(p), bool); inv[okp] = G[pi[okp], pj[okp]] >= 99; bad = int(inv.sum())
        if bad: ax.plot(p[inv, 0], p[inv, 1], 'x', color='yellow', mec='k', ms=9, mew=2.2, label='경로 위 무효 칸 %d' % bad)
    X, Y, TH = rec['pose']; c, s = math.cos(TH), math.sin(TH)
    fp = np.array([[0.262, 0.165], [0.262, -0.165], [-0.248, -0.165], [-0.248, 0.165], [0.262, 0.165]])
    ax.plot(X + c * fp[:, 0] - s * fp[:, 1], Y + s * fp[:, 0] + c * fp[:, 1], '-', color='lime', lw=2.5)
    ax.plot(1.6, -5.55, '*', color='r', ms=16); ax.text(1.7, -5.45, 'D', color='r', fontsize=13, fontweight='bold')
    for nm, (bx, by) in (('서 병목', (-1.64, -4.41)), ('가운데 병목', (0.96, -3.16)), ('동 병목', (3.31, -3.16))):
        ax.add_patch(plt.Circle((bx, by), 0.3, fill=False, ec='#444', ls='--', lw=1))
    nb = int((new_block & (wx > XL[0]) & (wx < XL[1]) & (wy > YL[0]) & (wy < YL[1])).sum())
    ax.set_xlim(*XL); ax.set_ylim(*YL); ax.grid(alpha=.25); ax.legend(loc='lower left', fontsize=8, framealpha=.85)
    ax.set_title('f2a8 D 구간 +%3.0f s | 경로 %s | 센서가 새로 막은 칸(자홍) %d | 경로 위 무효 칸 %d' % (rec['t'], classify(p), nb, bad), fontsize=11)
    fig.tight_layout(); fig.savefig(OUT + r'\f%03d.png' % k); plt.close(fig)
    stats.append((rec['t'], classify(p), nb, bad))
with open(OUT + r'\stats.csv', 'w', encoding='utf-8') as f:
    for s_ in stats: f.write('%.0f,%s,%d,%d\n' % s_)
print('프레임 %d' % len(stats))
