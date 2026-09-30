#!/usr/bin/env python3
"""09-30 §7: F0-b 주행 영상(1280×720, 10 fps = 실제 속도). 인자: vid_XXX.npz out.mp4 제목 [상자 전면 x] [상자 중심 y]
   왼쪽: 위에서 본 지도 — 배경 = 마지막 /map, 로컬 코스트맵(치명/팽창), 라이다 점, 전역 경로, 로버 외곽(실측 0.51×0.33), 지나온 궤적, 낮은 상자·문·W3.
   오른쪽: 경과 시간·실제 시각(KST, 촬영 영상과 맞추기용), 목표·단계, 속도 지령 그래프."""
import sys, math, subprocess, datetime
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle
from matplotlib import font_manager

for f in ('Malgun Gothic', 'NanumGothic', 'AppleGothic'):
    if any(f in x.name for x in font_manager.fontManager.ttflist): plt.rcParams['font.family'] = f; break
plt.rcParams['axes.unicode_minus'] = False

d = np.load(sys.argv[1]); OUT = sys.argv[2]; TITLE = sys.argv[3]
BX = float(sys.argv[4]) if len(sys.argv) > 4 else 1.15; BY = float(sys.argv[5]) if len(sys.argv) > 5 else -0.09
T = d['t']; P = d['pose']; N = len(T)
G = d['map']; mx, my, mr = d['map_meta']
plans = [d['plan_%d' % i] for i in range(int(d['n_plan']))]
lcms = [d['lcm_%d' % i] for i in range(int(d['n_lcm']))]; lmeta = d['lc_meta']
FX, BK, W2 = 0.262, -0.248, 0.165
GOALS = [(5.5, -2.2), (0.0, 0.0)]
bag_t0 = float(d['bag_t0']); kst = datetime.timezone(datetime.timedelta(hours=9))

xs, ys = P[:, 0], P[:, 1]
X0, X1, Y0, Y1 = xs.min() - 1.2, xs.max() + 1.2, ys.min() - 1.2, ys.max() + 1.2
fig = plt.figure(figsize=(12.8, 7.2), dpi=100, facecolor='#f4f5f3')
ax = fig.add_axes([0.02, 0.05, 0.64, 0.88]); ax.set_facecolor('#d7dad6')
bg = np.full(G.shape + (3,), 0.84); bg[G == 0] = 0.99; bg[G > 50] = 0.12
ax.imshow(bg, origin='lower', extent=[mx, mx + G.shape[1] * mr, my, my + G.shape[0] * mr], interpolation='nearest', zorder=0)
ax.set_xlim(X0, X1); ax.set_ylim(Y0, Y1); ax.set_aspect('equal')
ax.set_xticks(np.arange(math.ceil(X0), X1, 1)); ax.set_yticks(np.arange(math.ceil(Y0), Y1, 1)); ax.grid(color='#9fb0c8', lw=0.4, alpha=0.6)
ax.tick_params(labelsize=8, colors='#555')
ax.add_patch(Rectangle((BX, BY - 0.09), 0.11, 0.18, fill=False, ec='#c0266e', lw=1.8, ls='--', zorder=5))
ax.text(BX + 0.13, BY - 0.02, '낮은 상자\n(라이다 X)', fontsize=7, color='#c0266e', zorder=5)
ax.plot([1.85, 2.65], [-0.65, -0.65], color='#ef6c00', lw=3, zorder=5); ax.text(2.7, -0.72, '문 0.85 m', fontsize=9, color='#ef6c00', zorder=5)
for i, (gx, gy) in enumerate(GOALS):
    ax.plot(gx, gy, marker='*', ms=15, color='#e0a100', mec='#6b4d00', zorder=6)
    ax.text(gx + 0.12, gy + 0.12, ['W3 (목표 1)', '출발 (목표 2)'][i], fontsize=8, color='#6b4d00', zorder=6)
cm_leth = ax.scatter([], [], s=6, marker='s', c='#7b1fa2', alpha=0.55, lw=0, zorder=2)
cm_infl = ax.scatter([], [], s=6, marker='s', c='#ce93d8', alpha=0.35, lw=0, zorder=1.5)
scan = ax.scatter([], [], s=2.5, c='#e53935', lw=0, zorder=4)
plan_ln, = ax.plot([], [], color='#1f5fd1', lw=2, alpha=0.85, zorder=3)
trail, = ax.plot([], [], color='#2e7d32', lw=1.6, alpha=0.8, zorder=3)
body = Polygon(np.zeros((4, 2)), closed=True, fc='#1f5fd1', ec='#0d2f6b', alpha=0.55, lw=1.5, zorder=7); ax.add_patch(body)
head, = ax.plot([], [], color='#0d2f6b', lw=2, zorder=8)
ax.set_title(TITLE, fontsize=12, loc='left', color='#222')

# 오른쪽 정보
tx = fig.text(0.685, 0.86, '', fontsize=22, family='monospace', color='#111', weight='bold')
tk = fig.text(0.685, 0.80, '', fontsize=11, color='#333')
tp = fig.text(0.685, 0.72, '', fontsize=13, color='#1f5fd1', weight='bold')
ti = fig.text(0.685, 0.60, '', fontsize=10, color='#333', linespacing=1.5)
av = fig.add_axes([0.69, 0.10, 0.29, 0.30]); av.set_xlim(0, T[-1]); av.set_ylim(-0.45, 0.45)
av.axhline(0, color='#999', lw=0.6); av.set_xlabel('경과 s', fontsize=8); av.tick_params(labelsize=7); av.set_title('속도 지령', fontsize=9, loc='left')
lv, = av.plot([], [], color='#1f5fd1', lw=1.2, label='직진 v (m/s)'); lw_, = av.plot([], [], color='#c2410c', lw=1.2, label='회전 ω (rad/s)')
av.legend(fontsize=7, loc='upper right'); cur = av.axvline(0, color='#333', lw=0.8)
fig.text(0.685, 0.02, '출처: bag %s · 라이다 점(빨강) · 코스트맵(보라) · 전역 경로(파랑) · 궤적(초록)' % TITLE.split()[0], fontsize=7, color='#777')

v, w = d['v'], d['w']; pl_i, lc_f = d['pl_i'], d['lc_frame']; sidx = d['sidx']; SX, SY = d['sx'], d['sy']
t_act0 = float(d['t_act0'])
# 단계: 목표 1 → 정지 → 목표 2 (지령이 3 s 넘게 0 인 구간 = 정지)
moving = (np.abs(v) > 0.005) | (np.abs(w) > 0.01)
ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', '1280x720', '-r', '10', '-i', '-',
                       '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '20', OUT], stdin=subprocess.PIPE)
lcm_cache = {}
for k in range(N):
    x, y, th = P[k]; c, s = math.cos(th), math.sin(th)
    corners = [(FX, W2), (FX, -W2), (BK, -W2), (BK, W2)]
    body.set_xy([(x + c * a - s * b, y + s * a + c * b) for a, b in corners])
    head.set_data([x, x + c * 0.35], [y, y + s * 0.35])
    trail.set_data(xs[:k + 1], ys[:k + 1])
    scan.set_offsets(np.c_[SX[sidx[k]:sidx[k + 1]], SY[sidx[k]:sidx[k + 1]]])
    if pl_i[k] >= 0: pp = plans[pl_i[k]]; plan_ln.set_data(pp[:, 0], pp[:, 1]) if len(pp) else plan_ln.set_data([], [])
    j = lc_f[k]
    if j >= 0:
        if j not in lcm_cache:
            g = lcms[j]; ax0, ay0, ath, ox, oy, res = lmeta[j]
            ii, jj = np.nonzero(g >= 50); cx = ox + (jj + 0.5) * res; cy = oy + (ii + 0.5) * res
            ca, sa = math.cos(ath), math.sin(ath); mxp = ax0 + ca * cx - sa * cy; myp = ay0 + sa * cx + ca * cy
            L = g[ii, jj] >= 99; lcm_cache = {j: (np.c_[mxp[L], myp[L]], np.c_[mxp[~L], myp[~L]])}
        a, b = lcm_cache[j]; cm_leth.set_offsets(a); cm_infl.set_offsets(b)
    tt = T[k]; el = tt - t_act0
    tx.set_text('%+6.1f s' % el)
    tk.set_text('실제 시각 %s' % datetime.datetime.fromtimestamp(bag_t0 + tt, kst).strftime('%H:%M:%S.%f')[:-5])
    done1 = np.hypot(x - GOALS[0][0], y - GOALS[0][1]) < 0.2 or (k > 0 and np.any(np.hypot(xs[:k] - GOALS[0][0], ys[:k] - GOALS[0][1]) < 0.2))
    phase = '출발 전' if el < 0 else ('목표 1: W3 로' if not done1 else ('W3 도착 · 정지' if not moving[k] and np.hypot(x - GOALS[0][0], y - GOALS[0][1]) < 0.25 else '목표 2: 출발점으로'))
    if el > 0 and not moving[max(0, k - 1):k + 1].any() and np.hypot(x, y) < 0.2 and done1: phase = '복귀 완료'
    tp.set_text(phase)
    ti.set_text('위치 map (%+.2f, %+.2f) m\n방향 %+.0f°\n지령 v %+.3f m/s · ω %+.2f rad/s' % (x, y, math.degrees(th), v[k], w[k]))
    lv.set_data(T[:k + 1], v[:k + 1]); lw_.set_data(T[:k + 1], w[:k + 1]); cur.set_xdata([tt, tt])
    fig.canvas.draw(); ff.stdin.write(fig.canvas.buffer_rgba())
ff.stdin.close(); ff.wait(); print('완료', OUT, N, '프레임')
