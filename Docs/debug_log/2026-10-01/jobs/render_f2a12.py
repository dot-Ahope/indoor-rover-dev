# 10-01 §8.40: f2a12 전체 bag 시각화(1 s 간격) — 왼쪽 = 지도 전체·궤적, 오른쪽 = 로버 주변 3 × 3 m 확대.
#   빨강 = 라이다 스캔을 **기록된 로버 자세**로 지도에 놓은 것 → 지도 벽(검정)과 겹치면 자세가 맞고, 어긋나면 자세(또는 지도)가 틀린 것.
#   잔차 = 스캔 점 → 가장 가까운 지도 벽 거리 RMS(0.3 m 상한). 로컬 코스트맵·nvblox 는 odom → map 변환(map→odom 기록값).
import os, math, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from PIL import Image
from fit_scan import cost
plt.rcParams['font.family'] = 'Malgun Gothic'; plt.rcParams['axes.unicode_minus'] = False
SP = r'C:\Users\magma\AppData\Local\Temp\claude\F--6-Indoor-Rover-Rover\21d4aa9f-8412-4905-b23d-17554af330ea\scratchpad'
R = np.load(SP + r'\f2a6\f2a12_full.npz', allow_pickle=True)['recs']
im = np.array(Image.open(r'F:\6_Indoor_Rover\Rover\Docs\04_navigation\maps\office_v2.pgm')); mox, moy = -5.29, -6.96; MH, MW = im.shape
EXT = [mox, mox + MW * 0.05, moy, moy + MH * 0.05]
bg = np.where(im == 0, 0.15, np.where(im == 254, 1.0, 0.8))
FP = np.array([[0.262, 0.165], [0.262, -0.165], [-0.248, -0.165], [-0.248, 0.165], [0.262, 0.165]])
GOALS = [(2.25, -1.6), (-1.6, -2.0), (-1.65, -3.7), (-1.6, -5.5), (1.6, -5.55), (-1.6, -5.5), (-1.65, -3.7), (-1.6, -2.1), (5.5, -2.2), (0, 0)]
T0 = 5.0   # 추출 시작 = 러너 출발 5 s 전
OUT = SP + r'\f2a12viz'; os.makedirs(OUT, exist_ok=True)
traj = np.array([r['pose'][:2] for r in R])
for k, r in enumerate(R):
    X, Y, TH = r['pose']; c, s = math.cos(TH), math.sin(TH)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(16, 7.6), dpi=80, gridspec_kw={'width_ratios': [1.35, 1]})
    for ax in (a1, a2): ax.imshow(bg, cmap='gray', vmin=0, vmax=1, extent=EXT, interpolation='nearest')
    a1.plot(traj[:k + 1, 0], traj[:k + 1, 1], '-', color='#1f77b4', lw=1.5)
    for i, (gx, gy) in enumerate(GOALS): a1.plot(gx, gy, '*', color='r', ms=10); a1.text(gx + 0.1, gy + 0.1, str(i + 1), color='r', fontsize=9, fontweight='bold')
    a1.add_patch(plt.Rectangle((X - 1.5, Y - 1.5), 3, 3, fill=False, ec='orange', lw=1.5)); a1.set_xlim(EXT[0], EXT[1]); a1.set_ylim(EXT[2], EXT[3])
    a1.set_title('지도 office_v2 · 궤적(파랑) · 목표 1~10(빨강 별) · 주황 = 오른쪽 확대 영역', fontsize=10)
    # 로컬 코스트맵·nvblox (odom → map)
    tx, ty, tw = r['mo']; cc, ss = math.cos(tw), math.sin(tw)
    lc = r['gcm'].astype(float); lox, loy, lres = r['gcm_o']
    for th, hi, col in ((99, 101, (0.85, 0, 0.75, 0.55)), (50, 99, (1, 0.6, 0.9, 0.35))):
        ii, jj = np.where((lc >= th) & (lc < hi)); ox_, oy_ = lox + (jj + .5) * lres, loy + (ii + .5) * lres
        a2.scatter(tx + cc * ox_ - ss * oy_, ty + ss * ox_ + cc * oy_, s=30, marker='s', color=col, lw=0)
    if 'nv' in r:
        nv = r['nv']; nox, noy, nres, unk = r['nv_o']; oi, oj = np.where((nv <= 0.05) & (nv < unk * 0.5)); ox_, oy_ = nox + (oj + .5) * nres, noy + (oi + .5) * nres
        a2.plot(tx + cc * ox_ - ss * oy_, ty + ss * ox_ + cc * oy_, 's', ms=2.2, color='#ff8c00', label='카메라(nvblox) 장애물')
    p = r.get('plan')
    if p is not None and len(p): a2.plot(p[:, 0], p[:, 1], '-', color='#00b7eb', lw=2, label='전역 경로')
    a2.plot(r['scan'][:, 0], r['scan'][:, 1], '.', ms=3, color='r', label='라이다(기록 자세로 배치)')
    a2.plot(X + c * FP[:, 0] - s * FP[:, 1], Y + s * FP[:, 0] + c * FP[:, 1], '-', color='lime', lw=2.5, label='로버(추정 자세)')
    a2.annotate('', xy=(X + 0.35 * c, Y + 0.35 * s), xytext=(X, Y), arrowprops=dict(arrowstyle='->', color='lime', lw=2))
    for gx, gy in GOALS: a2.plot(gx, gy, '*', color='r', ms=14)
    a2.set_xlim(X - 1.5, X + 1.5); a2.set_ylim(Y - 1.5, Y + 1.5); a2.set_aspect('equal'); a2.grid(alpha=.25); a2.legend(loc='lower left', fontsize=7, framealpha=.85)
    sc = r['scan'].astype(float); sc = sc[np.hypot(sc[:, 0] - X, sc[:, 1] - Y) < 4.0]; res = cost([0, 0, 0], sc, X, Y) ** .5
    a2.set_title('확대 3 × 3 m — 검정 = 저장 지도 벽, 자홍 = 로컬 ≥ 내접 | 스캔-지도 잔차 %.3f m' % res, fontsize=10)
    fig.suptitle('f2a12 +%5.1f s  로버 (%.2f, %.2f, %.0f°)' % (r['t'] - T0, X, Y, math.degrees(TH)), fontsize=12)
    fig.tight_layout(); fig.savefig(OUT + r'\f%03d.png' % k); plt.close(fig)
print('프레임', len(R))
