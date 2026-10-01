# 10-01 §8.37: f2a12 목표 7(서쪽 통로 북행) — 출발 직후 왜 제자리에서 떨기만 했나. 왼쪽 전역, 오른쪽 로컬(+nvblox·라이다), 아래 바퀴 명령.
import math, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from PIL import Image
from scipy import ndimage
plt.rcParams['font.family'] = 'Malgun Gothic'; plt.rcParams['axes.unicode_minus'] = False
SP = r'C:\Users\magma\AppData\Local\Temp\claude\F--6-Indoor-Rover-Rover\21d4aa9f-8412-4905-b23d-17554af330ea\scratchpad'
G = np.load(SP + r'\f2a6\f2a12_gviz.npz', allow_pickle=True)['recs']; L = np.load(SP + r'\f2a6\f2a12_lviz.npz', allow_pickle=True)['recs']
C = np.load(SP + r'\f2a6\f2a12_g7.npz', allow_pickle=True); plan = C['plans'][-1]; cmd = C['cmd_vel']
im = np.array(Image.open(r'F:\6_Indoor_Rover\Rover\Docs\04_navigation\maps\office_v2.pgm')); mr = 0.05; mox, moy = -5.29, -6.96; MH, MW = im.shape
d = ndimage.distance_transform_edt(im != 0) * mr
base = np.where(d <= 0.175, 253, np.where(d <= 0.70, 252 * np.exp(-2.0 * (d - 0.175)), 0)); base[im == 0] = 254
baseO = np.where(base >= 254, 100, np.where(base >= 253, 99, np.where(base <= 0, 0, 1 + 97 * (base - 1) / 251)))
yy, xx = np.mgrid[0:MH, 0:MW]; wx = mox + (xx + 0.5) * mr; wy = moy + (MH - 1 - yy + 0.5) * mr
XL, YL = (-2.4, -0.4), (-6.0, -3.5); EXT = [mox, mox + MW * mr, moy, moy + MH * mr]
FP = np.array([[0.262, 0.165], [0.262, -0.165], [-0.248, -0.165], [-0.248, 0.165], [0.262, 0.165]])
def robot(ax, pose):
    X, Y, TH = pose; c, s = math.cos(TH), math.sin(TH)
    ax.plot(X + c * FP[:, 0] - s * FP[:, 1], Y + s * FP[:, 0] + c * FP[:, 1], '-', color='lime', lw=2.5)
    ax.annotate('', xy=(X + 0.3 * c, Y + 0.3 * s), xytext=(X, Y), arrowprops=dict(arrowstyle='->', color='lime', lw=2))
def common(ax, rec):
    ax.plot(rec['scan'][:, 0], rec['scan'][:, 1], '.', ms=2.5, color='r', label='라이다(0.185 m 높이)')
    ax.plot(plan[:, 0], plan[:, 1], '-', color='#00b7eb', lw=2.2, label='전역 경로(1 회 계획)')
    robot(ax, rec['pose']); ax.plot(-1.65, -3.7, '*', color='r', ms=15); ax.text(-1.55, -3.65, '목표 7', color='r', fontsize=10, fontweight='bold')
    ax.set_xlim(*XL); ax.set_ylim(*YL); ax.set_aspect('equal'); ax.grid(alpha=.25)
for k in (2, 10, 40):
    g, l = G[k], L[k]
    fig = plt.figure(figsize=(14, 10), dpi=85); a1 = fig.add_subplot(2, 2, 1); a2 = fig.add_subplot(2, 2, 2); a3 = fig.add_subplot(2, 1, 2)
    gg = g['gcm'].astype(float); gox, goy, gres = g['gcm_o']; GH, GW = gg.shape
    gi = ((wy - goy) / gres).astype(int); gj = ((wx - gox) / gres).astype(int); ok = (gi >= 0) & (gi < GH) & (gj >= 0) & (gj < GW)
    Gm = np.full((MH, MW), -1.0); Gm[ok] = gg[gi[ok], gj[ok]]; nb = (Gm >= 99) & (baseO < 99)
    bg = np.ones((MH, MW, 3)) * (1 - baseO[..., None] / 100 * 0.75); bg[im == 0] = 0.1
    a1.imshow(bg, extent=EXT, interpolation='nearest'); ov = np.zeros((MH, MW, 4)); ov[nb] = (0.85, 0, 0.75, 0.75); a1.imshow(ov, extent=EXT, interpolation='nearest')
    common(a1, g); a1.legend(loc='lower left', fontsize=7); a1.set_title('전역 — 회색 = 저장 지도 비용, 자홍 = 센서가 새로 막은 칸', fontsize=9)
    bg2 = np.ones((MH, MW, 3)) * 0.85; bg2[im == 254] = 1; bg2[im == 0] = 0.2; a2.imshow(bg2, extent=EXT, interpolation='nearest')
    # 로컬 코스트맵·nvblox 슬라이스는 odom 좌표 → 기록된 map→odom(tx, ty, yaw)으로 map 좌표에 옮겨 그린다(10-01 §8.37 정정)
    tx, ty, tyaw = l['mo']; cc, ss = math.cos(tyaw), math.sin(tyaw)
    def o2m(x, y): return tx + cc * x - ss * y, ty + ss * x + cc * y
    lc = l['gcm'].astype(float); lox, loy, lres = l['gcm_o']
    for th, col, lab in ((99, (0.85, 0, 0.75, 0.8), '로컬 ≥ 내접'), (50, (1, 0.6, 0.9, 0.5), '로컬 50~98')):
        ii, jj = np.where((lc >= th) & (lc < (101 if th == 99 else 99)))
        mx, my = o2m(lox + (jj + .5) * lres, loy + (ii + .5) * lres); a2.scatter(mx, my, s=26, marker='s', color=col, label=lab, lw=0)
    nv = l['nv']; nox, noy, nres, unk = l['nv_o']; oi, oj = np.where((nv <= 0.05) & (nv < unk * 0.5))
    mx, my = o2m(nox + (oj + .5) * nres, noy + (oi + .5) * nres); a2.plot(mx, my, 's', ms=2.5, color='#ff8c00', label='카메라(nvblox) 장애물')
    common(a2, l); a2.legend(loc='lower left', fontsize=7); a2.set_title('로컬(MPPI) — 자홍 ≥ 내접, 연분홍 50~98', fontsize=9)
    a3.plot(cmd[:, 0], cmd[:, 1] * 10, '-', color='#1f77b4', lw=1, label='전진 지령 vx × 10 (m/s)'); a3.plot(cmd[:, 0], cmd[:, 2], '-', color='#d62728', lw=1, label='회전 지령 wz (rad/s)')
    a3.axvline(l['t'], color='k', ls='--'); a3.axhline(0, color='#888', lw=.6); a3.set_xlabel('목표 7 시작 후 (s)'); a3.legend(loc='upper right', fontsize=8); a3.grid(alpha=.25)
    a3.set_title('MPPI 바퀴 지령 — 9 s 이후 전진 ±0.015 m/s·회전 ±0.2 rad/s 가 3 s 에 4~8 번 부호를 바꿈(떨림), 실제 이동 ≈ 0', fontsize=9)
    fig.suptitle('f2a12 목표 7(서쪽 통로 북행) +%.0f s — 로버 (%.2f, %.2f, %.0f°)' % (l['t'], *l['pose'][:2], math.degrees(l['pose'][2])), fontsize=12)
    fig.tight_layout(); fig.savefig(SP + r'\g7_%02d.png' % k); plt.close(fig)
print('ok')
