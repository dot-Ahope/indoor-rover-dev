#!/usr/bin/env python3
"""10-07 §9 쇼케이스: bag 구간(job930_extract npz) → 위에서 본 데이터 영상(720×720, 10 fps = 실제 속도).
   인자: npz out.mp4 시작KST(HH:MM:SS) 길이s 제목 자막json
   자막json: [["HH:MM:SS", "문구"], ...] — 그 시각부터 다음 자막 전까지 표시.
   그림: 배경 = 저장 지도(/map), 전역 코스트맵 고비용(계획기가 보는 장애물), 로컬 코스트맵 치명 칸(MPPI 가 보는 장애물, odom→map 변환),
         라이다 점, 전역 경로(점선), 지나온 궤적, 로버 외곽(0.51×0.33 m)·진행 방향, 아래 지령 v·ω 막대.
   시각: Jetson epoch 1791346297 = 13:11:37 KST(같은 날 bag·러너 로그로 맞춤). 실제 영상은 휴대폰 파일 이름 시각(네트워크 시각, ±1~2 s 가정)."""
import sys, json, math, subprocess, textwrap
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib import font_manager
for f in ('Malgun Gothic', 'NanumGothic'):
    if any(f in x.name for x in font_manager.fontManager.ttflist): plt.rcParams['font.family'] = f; break
plt.rcParams['axes.unicode_minus'] = False
BG, INK, INK2 = '#15161a', '#e8eaed', '#9aa0a6'
C_ROVER, C_TRAIL, C_PLAN, C_SCAN, C_LOC, C_GLB = '#4e98e2', '#3ddc84', '#b388ff', '#ff5252', '#ff4fd8', '#f5a623'
XF, XB, HW, LX, LY = 0.262, -0.248, 0.165, 0.152, math.pi - 0.04677
E0, K0 = 1791346297.0, 13 * 3600 + 11 * 60 + 37
def kst2e(s): h, m, x = map(int, s.split(':')); return E0 + h * 3600 + m * 60 + x - K0
def e2kst(e): s = int(round(e - E0 + K0)); return '%02d:%02d:%02d' % (s // 3600, s // 60 % 60, s % 60)

Z = np.load(sys.argv[1]); OUT = sys.argv[2]; TA = kst2e(sys.argv[3]); DUR = float(sys.argv[4]); TITLE = sys.argv[5]
CAP = [(kst2e(a), b) for a, b in json.load(open(sys.argv[6], encoding='utf-8'))]
tr, mo, cmd = Z['traj'], Z['mo'], Z['cmd']; pt, pn, pxy = Z['plan_t'], Z['plan_n'], Z['plan_xy']; off = np.r_[0, np.cumsum(pn)]
M = Z['map'].astype(float); mres, mox, moy = Z['map_meta']
mimg = np.where(M < 0, 0.18, np.where(M >= 50, 0.75, 0.08))
def last(ts, t): i = np.searchsorted(ts, t) - 1; return i if i >= 0 else None
def pose(t): j = min(max(np.searchsorted(tr[:, 0], t), 0), len(tr) - 1); return tr[j, 1:]
def m2(t): i = min(max(np.searchsorted(mo[:, 0], t), 0), len(mo) - 1); return mo[i, 1:]
W = H = 720; fig = plt.figure(figsize=(W / 100, H / 100), dpi=100, facecolor=BG)
ax = fig.add_axes([0.0, 0.17, 1.0, 0.68]); axv = fig.add_axes([0.08, 0.035, 0.38, 0.05]); axw = fig.add_axes([0.56, 0.035, 0.38, 0.05])
ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', '%dx%d' % (W, H), '-r', '10', '-i', '-',
                       '-c:v', 'libx264', '-crf', '22', '-pix_fmt', 'yuv420p', OUT], stdin=subprocess.PIPE)
trail = []
for k in range(int(DUR * 10)):
    t = TA + k / 10.0; x, y, th = pose(t); trail.append((x, y))
    ax.clear(); ax.set_facecolor(BG); R = 1.9
    ax.imshow(mimg, origin='lower', cmap='gray', vmin=0, vmax=1, extent=[mox, mox + M.shape[1] * mres, moy, moy + M.shape[0] * mres], interpolation='nearest')
    i = last(Z['gcm_t'], t)
    if i is not None:
        g = Z['gcm'][i]; r, ox, oy = Z['gcm_meta'][i]; iy, ix = np.nonzero(g >= 100)   # 치명 칸만(내접 띠는 화면을 덮어 뺌)
        ax.scatter(ox + (ix + .5) * r, oy + (iy + .5) * r, s=30, marker='s', facecolors='none', edgecolors=C_GLB, linewidths=1.0, alpha=0.9)
    i = last(Z['lcm_t'], t)
    if i is not None:
        g = Z['lcm'][i]; r, ox, oy = Z['lcm_meta'][i]; iy, ix = np.nonzero(g >= 100); wx, wy = ox + (ix + .5) * r, oy + (iy + .5) * r
        mx, my, mth = m2(Z['lcm_t'][i]); c, s = math.cos(mth), math.sin(mth)
        ax.scatter(mx + c * wx - s * wy, my + s * wx + c * wy, s=14, marker='s', c=C_LOC, alpha=0.85, linewidths=0)
    i = last(Z['scan_t'], t)
    if i is not None:
        rr = Z['scan_r'][i]; a0, da = Z['scan_a'][i]; a = a0 + da * np.arange(len(rr)) + LY; ok = np.isfinite(rr) & (rr > .05) & (rr < 4)
        px, py, pth = pose(Z['scan_t'][i]); bx, by = LX + rr[ok] * np.cos(a[ok]), rr[ok] * np.sin(a[ok]); c, s = math.cos(pth), math.sin(pth)
        ax.scatter(px + c * bx - s * by, py + s * bx + c * by, s=3, c=C_SCAN, linewidths=0)
    i = last(pt, t)
    if i is not None: P = pxy[off[i]:off[i + 1]]; ax.plot(P[:, 0], P[:, 1], '--', color=C_PLAN, lw=1.6)
    T_ = np.array(trail); ax.plot(T_[:, 0], T_[:, 1], color=C_TRAIL, lw=1.6)
    c, s = math.cos(th), math.sin(th); C = np.array([[XF, HW], [XF, -HW], [XB, -HW], [XB, HW]])
    ax.add_patch(Polygon(np.c_[x + c * C[:, 0] - s * C[:, 1], y + s * C[:, 0] + c * C[:, 1]], closed=True, fc=C_ROVER, ec='white', lw=1.2, alpha=0.75))
    ax.annotate('', (x + 0.4 * c, y + 0.4 * s), (x, y), arrowprops=dict(arrowstyle='->', color='white', lw=1.6))
    ax.set_xlim(x - R, x + R); ax.set_ylim(y - R, y + R); ax.set_aspect('equal'); ax.axis('off')
    for t_ in fig.texts[:]: t_.remove()
    fig.text(0.02, 0.965, TITLE, color=INK, fontsize=15, weight='bold', va='top')
    fig.text(0.98, 0.965, '%s KST' % e2kst(t), color=INK2, fontsize=12, va='top', ha='right')
    cap = [b for a, b in CAP if a <= t]
    if cap: fig.text(0.02, 0.918, '\n'.join(textwrap.wrap(cap[-1], 46)), color='#ffd666', fontsize=12, va='top', linespacing=1.3)
    fig.text(0.02, 0.135, '■ 로컬 치명 칸(MPPI)', color=C_LOC, fontsize=10); fig.text(0.27, 0.135, '□ 전역 치명 칸(계획기)', color=C_GLB, fontsize=10)
    fig.text(0.53, 0.135, '· 라이다', color=C_SCAN, fontsize=10); fig.text(0.65, 0.135, '-- 계획 경로', color=C_PLAN, fontsize=10); fig.text(0.83, 0.135, '— 궤적', color=C_TRAIL, fontsize=10)
    j = last(cmd[:, 0], t); v, w = (cmd[j, 1], cmd[j, 2]) if j is not None and t - cmd[j, 0] < 0.5 else (0.0, 0.0)
    for a_, val, lim, lab in ((axv, v, 0.1, '지령 v %+.3f m/s'), (axw, w, 0.4, '지령 ω %+.2f rad/s')):
        a_.clear(); a_.set_facecolor('#2a2c33'); a_.barh([0], [val], color=C_ROVER if abs(val) > 1e-3 else INK2); a_.set_xlim(-lim, lim); a_.axvline(0, color=INK2, lw=0.8)
        a_.set_yticks([]); a_.set_xticks([]); [sp.set_visible(False) for sp in a_.spines.values()]; a_.set_title(lab % val, color=INK, fontsize=10, pad=3)
    fig.canvas.draw(); ff.stdin.write(np.asarray(fig.canvas.buffer_rgba()).tobytes())
ff.stdin.close(); ff.wait(); print('ok', OUT, int(DUR * 10), '프레임')
