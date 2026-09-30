#!/usr/bin/env python3
"""09-30 §7.2: F0-b 주행 영상 v2(1280×720, 10 fps = 실제 속도). 인자: vid_XXX.npz out.mp4 제목 [상자 전면 x] [상자 중심 y]
   왼쪽: 위에서 본 지도 — 배경 /map, 로컬 코스트맵, 라이다 점, 전역 경로(점선), 로버(실측 0.51×0.33, 방향 화살표), 지나온 궤적,
         목표 링·라벨 상자, 낮은 상자, 문, 범례.
   오른쪽: 경과 s·실제 시각(KST), 단계 칩, 수치, 직진·회전 속도 — /cmd_vel 명령(실선) vs EKF 실제(점선), /cmd_vel 발행 주기(Hz)."""
import sys, math, subprocess, datetime
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle, Circle, FancyArrow, FancyBboxPatch
from matplotlib.lines import Line2D
from matplotlib import font_manager

for f in ('Malgun Gothic', 'NanumGothic', 'AppleGothic'):
    if any(f in x.name for x in font_manager.fontManager.ttflist): plt.rcParams['font.family'] = f; break
plt.rcParams['axes.unicode_minus'] = False

INK, INK2, BG, PANEL = '#e8eaed', '#9aa0a6', '#15161a', '#1f2126'   # 09-30 v3: Foxglove 풍 어두운 테마(사용자 요청)
C_ROVER, C_TRAIL, C_PLAN, C_SCAN = '#4e98e2', '#3ddc84', '#b388ff', '#ff5252'
C_LETH, C_INFL, C_GOAL, C_BOX, C_DOOR, C_ACT = '#ff4fd8', '#2d6f9e', '#ffc53d', '#ff7aa8', '#ff9f43', '#c8ccd2'

d = np.load(sys.argv[1]); OUT = sys.argv[2]; TITLE = sys.argv[3]
BX = float(sys.argv[4]) if len(sys.argv) > 4 else 1.15; BY = float(sys.argv[5]) if len(sys.argv) > 5 else -0.09
T = d['t']; P = d['pose']; N = len(T)
G = d['map']; mx, my, mr = d['map_meta']
plans = [d['plan_%d' % i] for i in range(int(d['n_plan']))]
lcms = [d['lcm_%d' % i] for i in range(int(d['n_lcm']))]; lmeta = d['lc_meta']
FX, BK, W2 = 0.262, -0.248, 0.165
GOALS = [(5.5, -2.2, 'W3', '목표 1'), (0.0, 0.0, '출발', '목표 2')]
bag_t0 = float(d['bag_t0']); kst = datetime.timezone(datetime.timedelta(hours=9))
v, w, ov, ow, hz = d['v'], d['w'], d['ov'], d['ow'], d['hz']
t_act0 = float(d['t_act0']); EL = T - t_act0

xs, ys = P[:, 0], P[:, 1]
X0, X1, Y0, Y1 = xs.min() - 1.2, xs.max() + 1.2, ys.min() - 1.2, ys.max() + 1.2
fig = plt.figure(figsize=(12.8, 7.2), dpi=100, facecolor=BG)
ax = fig.add_axes([0.015, 0.04, 0.655, 0.86]); ax.set_facecolor('#101114')
bg = np.zeros(G.shape + (3,)); bg[:] = (0.06, 0.065, 0.08); bg[G == 0] = (0.17, 0.18, 0.21); bg[G > 50] = (0.80, 0.83, 0.88)
ax.imshow(bg, origin='lower', extent=[mx, mx + G.shape[1] * mr, my, my + G.shape[0] * mr], interpolation='nearest', zorder=0)
ax.set_xlim(X0, X1); ax.set_ylim(Y0, Y1); ax.set_aspect('equal')
ax.set_xticks(np.arange(math.ceil(X0), X1, 1)); ax.set_yticks(np.arange(math.ceil(Y0), Y1, 1))
ax.grid(color='#3a3f4b', lw=0.5, alpha=0.9); ax.tick_params(labelsize=7, colors=INK2, length=0)
for sp in ax.spines.values(): sp.set_edgecolor('#2c2f36')
ax.text(X1 - 0.05, Y0 + 0.08, '격자 1 m', fontsize=7, color=INK2, ha='right')


def label(x, y, txt, color, dx=0.18, dy=0.18):
    ax.text(x + dx, y + dy, txt, fontsize=8, color=color, weight='bold', zorder=9, clip_on=True,
            bbox=dict(boxstyle='round,pad=0.2,rounding_size=0.3', fc='#1f2126', ec=color, lw=0.8, alpha=0.9))


# 목표: 이중 링 + 중심점 + 라벨 상자
for gx, gy, nm, sub in GOALS:
    ax.add_patch(Circle((gx, gy), 0.08, fill=False, ec=C_GOAL, lw=1.4, zorder=6))   # 09-30 v3: 표시 축소(사용자: 너무 큼)
    ax.add_patch(Circle((gx, gy), 0.02, fc=C_GOAL, ec='none', zorder=6))
    label(gx, gy, '%s · %s' % (nm, sub), C_GOAL, dx=0.10, dy=0.10)
# 낮은 상자(라이다에 안 보임) · 문
ax.add_patch(Rectangle((BX, BY - 0.09), 0.11, 0.18, fc='none', ec=C_BOX, lw=1.2, ls='--', zorder=5))
label(BX + 0.05, BY + 0.09, '낮은 상자 11 cm', C_BOX, dx=-0.35, dy=0.14)
ax.plot([1.85, 2.65], [-0.65, -0.65], color=C_DOOR, lw=3.2, solid_capstyle='round', zorder=5)
label(2.25, -0.65, '문 0.85 m', C_DOOR, dx=0.45, dy=-0.12)

cm_infl = ax.scatter([], [], s=5, marker='s', c=C_INFL, alpha=0.45, lw=0, zorder=1.5)
cm_leth = ax.scatter([], [], s=5, marker='s', c=C_LETH, alpha=0.6, lw=0, zorder=2)
scan = ax.scatter([], [], s=2.2, c=C_SCAN, lw=0, zorder=4)
plan_ln, = ax.plot([], [], color=C_PLAN, lw=1.8, ls=(0, (5, 3)), alpha=0.9, zorder=3)
trail, = ax.plot([], [], color=C_TRAIL, lw=2.0, alpha=0.9, solid_capstyle='round', zorder=3)
body = Polygon(np.zeros((4, 2)), closed=True, fc=C_ROVER, ec='#cfe4ff', alpha=0.45, lw=1.2, joinstyle='round', zorder=7); ax.add_patch(body)
arrow = [None]
ax.legend(handles=[Line2D([], [], color=C_TRAIL, lw=2, label='지나온 궤적'), Line2D([], [], color=C_PLAN, lw=1.8, ls='--', label='전역 경로'),
                   Line2D([], [], marker='o', ls='', color=C_SCAN, ms=4, label='라이다 점'), Line2D([], [], marker='s', ls='', color=C_LETH, ms=6, label='장애물(코스트맵)'),
                   Line2D([], [], marker='s', ls='', color=C_INFL, ms=6, label='여유 구역')],
          loc='lower left', fontsize=7, frameon=True, framealpha=0.9, facecolor='#1f2126', edgecolor='#34373e', labelcolor=INK, ncol=5, handlelength=1.6, columnspacing=1.0)
fig.text(0.015, 0.935, TITLE, fontsize=13, color=INK, weight='bold')

# 오른쪽 패널
fig.patches.append(FancyBboxPatch((0.685, 0.525), 0.300, 0.40, boxstyle='round,pad=0.006,rounding_size=0.012', transform=fig.transFigure, fc=PANEL, ec='#34373e', lw=0.8))
fig.text(0.70, 0.885, '출발 기준 경과', fontsize=8, color=INK2)
tx = fig.text(0.70, 0.815, '', fontsize=26, color=INK, weight='bold', family='DejaVu Sans Mono')
tk = fig.text(0.70, 0.785, '', fontsize=9, color=INK2)
chip = fig.text(0.70, 0.725, '', fontsize=11, color='white', weight='bold',
                bbox=dict(boxstyle='round,pad=0.35,rounding_size=0.6', fc=C_ROVER, ec='none'))
ti = fig.text(0.70, 0.555, '', fontsize=9, color=INK, linespacing=1.55)


def speed_ax(rect, title, ylim, unit):
    a = fig.add_axes(rect); a.set_facecolor('#1a1b20'); a.set_xlim(EL[0], EL[-1]); a.set_ylim(*ylim)
    a.axhline(0, color='#5f6570', lw=0.6); a.grid(color='#2c2f36', lw=0.5); a.tick_params(labelsize=7, colors=INK2, length=0)
    for sp in a.spines.values(): sp.set_edgecolor('#34373e')
    a.set_title(title, fontsize=9, loc='left', color=INK, pad=3); a.set_ylabel(unit, fontsize=7, color=INK2)
    return a


a1 = speed_ax([0.705, 0.30, 0.275, 0.17], '직진 속도', (-0.1, 0.1), 'm/s')
a2 = speed_ax([0.705, 0.075, 0.275, 0.17], '회전 속도', (-0.6, 0.6), 'rad/s'); a2.set_xlabel('출발 기준 경과 s', fontsize=7, color=INK2)
for a, lim, lbl in ((a1, 0.08, '명령 상한 0.08'), (a2, 0.38, '명령 상한 ±0.38')):
    a.axhline(lim, color=C_GOAL, lw=0.7, ls=':'); a.text(EL[-1], lim, lbl + ' ', fontsize=6, color=C_GOAL, ha='right', va='bottom')
    if a is a2: a.axhline(-lim, color=C_GOAL, lw=0.7, ls=':')
l1c, = a1.plot([], [], color=C_ROVER, lw=1.3, label='/cmd_vel 명령'); l1a, = a1.plot([], [], color=C_ACT, lw=1.0, ls='--', label='실제(EKF)')
l2c, = a2.plot([], [], color='#f5774d', lw=1.3, label='/cmd_vel 명령'); l2a, = a2.plot([], [], color=C_ACT, lw=1.0, ls='--', label='실제(EKF)')
a1.legend(fontsize=6, loc='lower right', frameon=False, ncol=2, labelcolor=INK); a2.legend(fontsize=6, loc='lower right', frameon=False, ncol=2, labelcolor=INK)
c1 = a1.axvline(0, color=INK, lw=0.7); c2 = a2.axvline(0, color=INK, lw=0.7)
fig.text(0.985, 0.012, '출처: bag %s · /cmd_vel·/odometry/filtered·/scan·/plan·/local_costmap' % TITLE.split()[0], fontsize=6.5, color='#6b7079', ha='right')

moving = (np.abs(v) > 0.005) | (np.abs(w) > 0.01)
ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', '1280x720', '-r', '10', '-i', '-',
                       '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '20', OUT], stdin=subprocess.PIPE)
lcm_cache = {}; sidx = d['sidx']; SX, SY = d['sx'], d['sy']; pl_i, lc_f = d['pl_i'], d['lc_frame']
reached1 = False
for k in range(N):
    x, y, th = P[k]; c, s = math.cos(th), math.sin(th)
    body.set_xy([(x + c * a - s * b, y + s * a + c * b) for a, b in [(FX, W2), (FX, -W2), (BK, -W2), (BK, W2)]])
    if arrow[0]: arrow[0].remove()
    arrow[0] = ax.add_patch(FancyArrow(x, y, c * 0.20, s * 0.20, width=0.035, head_width=0.11, head_length=0.08, fc='#cfe4ff', ec='#0b2a63', lw=0.6, zorder=8))
    trail.set_data(xs[:k + 1], ys[:k + 1])
    scan.set_offsets(np.c_[SX[sidx[k]:sidx[k + 1]], SY[sidx[k]:sidx[k + 1]]])
    if pl_i[k] >= 0 and len(plans[pl_i[k]]): pp = plans[pl_i[k]]; plan_ln.set_data(pp[:, 0], pp[:, 1])
    j = lc_f[k]
    if j >= 0:
        if j not in lcm_cache:
            g = lcms[j]; ax0, ay0, ath, ox, oy, res = lmeta[j]
            ii, jj = np.nonzero(g >= 50); cx = ox + (jj + 0.5) * res; cy = oy + (ii + 0.5) * res
            ca, sa = math.cos(ath), math.sin(ath); mxp = ax0 + ca * cx - sa * cy; myp = ay0 + sa * cx + ca * cy
            L = g[ii, jj] >= 99; lcm_cache = {j: (np.c_[mxp[L], myp[L]], np.c_[mxp[~L], myp[~L]])}
        a_, b_ = lcm_cache[j]; cm_leth.set_offsets(a_); cm_infl.set_offsets(b_)
    el = EL[k]
    reached1 = reached1 or math.hypot(x - GOALS[0][0], y - GOALS[0][1]) < 0.2
    if el < 0: ph, col = '출발 전', '#5f6570'
    elif not reached1: ph, col = '목표 1 · W3 로', C_ROVER
    elif not moving[k] and math.hypot(x - GOALS[0][0], y - GOALS[0][1]) < 0.25: ph, col = 'W3 도착 · 정지 3 s', C_GOAL
    elif math.hypot(x, y) < 0.2 and not moving[k]: ph, col = '복귀 완료', '#2e9d5b'
    else: ph, col = '목표 2 · 출발점으로', '#0e7c86'
    tx.set_text('%+7.1f s' % el)
    tk.set_text('실제 시각 %s (KST)' % datetime.datetime.fromtimestamp(bag_t0 + T[k], kst).strftime('%H:%M:%S.%f')[:-5])
    chip.set_text(' %s ' % ph); chip.get_bbox_patch().set_facecolor(col)
    ti.set_text('위치  map (%+.2f, %+.2f) m    방향 %+.0f°\n명령  v %+.3f m/s   ω %+.2f rad/s\n실제  v %+.3f m/s   ω %+.2f rad/s\n/cmd_vel 발행  %d Hz' % (x, y, math.degrees(th), v[k], w[k], ov[k], ow[k], hz[k]))
    l1c.set_data(EL[:k + 1], v[:k + 1]); l1a.set_data(EL[:k + 1], ov[:k + 1]); l2c.set_data(EL[:k + 1], w[:k + 1]); l2a.set_data(EL[:k + 1], ow[:k + 1])
    c1.set_xdata([el, el]); c2.set_xdata([el, el])
    fig.canvas.draw(); ff.stdin.write(fig.canvas.buffer_rgba())
ff.stdin.close(); ff.wait(); print('완료', OUT, N, '프레임')
