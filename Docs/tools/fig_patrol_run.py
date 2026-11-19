#!/usr/bin/env python3
"""fig_patrol_run — 순회 주행 한 번(러너 위치 기록 csv + 러너 로그)을 저장 지도 위 GIF · mp4 로(스타일 D). 11-19 jobs/fig_readme_patrol_1119 의 상시판(2026-11-19 §2).
  왜: README '자율주행' 순회 그림을 다른 주행으로도 만들 수 있게(주행 폴더를 인자로), 지도 읽기는 lib_rover 로(도구 겹침 정리).
      목표 계획만 그리는 정지 그림은 fig_patrol_goals(러너 문자열 입력) — 이것은 '실제로 달린 한 번'.
  로버 움직임: 없음. 입력: 주행 폴더의 <이름>.csv(t · map_x · map_y · map_yaw · goal) · f0_<이름>.log(목표 목록 · 'SUCCEEDED').
  사용: fig_patrol_run.py 주행폴더 출력.gif [--speed 40] [--map office_v3] [--fps 5]   예) Docs/debug_log/2026-11-11/bags/f0_f2rr1
  출력: 지정 파일 + 표준 출력에 목표 수 · 성공 수."""
import argparse, math, re, sys
from pathlib import Path
import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
sys.path.insert(0, str(Path(__file__).resolve().parent)); import lib_rover as L

ap = argparse.ArgumentParser(); ap.add_argument('run'); ap.add_argument('out')
ap.add_argument('--speed', type=float, default=40.0); ap.add_argument('--map', default='office_v3'); ap.add_argument('--fps', type=int, default=5)
A = ap.parse_args(); RUN = Path(A.run); NAME = RUN.name.replace('f0_', ''); L.style_d()
d = np.genfromtxt(RUN / f'{NAME}.csv', delimiter=',', names=True)
t, x, y, yaw, g = d['t'], d['map_x'], d['map_y'], d['map_yaw'], d['goal'].astype(int)
log = (RUN / f'f0_{NAME}.log').read_text(encoding='utf-8')
goals = [(float(a), float(b)) for a, b in re.findall(r'\(([-\d.]+), ([-\d.]+), \'[pf]\'\)', log.split('→')[0])]
NG = int(g.max()); goals = goals[:NG]; ok = len(re.findall(r'목표 \d+ SUCCEEDED', log))
print('goals', len(goals), 'succeeded', ok)

fig, ax = plt.subplots(figsize=(6.4, 5.4), dpi=100); L.draw_map(ax, A.map)
xs, ys = np.r_[x, [p[0] for p in goals]], np.r_[y, [p[1] for p in goals]]
ax.set_xlim(xs.min() - 0.6, xs.max() + 0.6); ax.set_ylim(ys.min() - 0.6, ys.max() + 0.6); L.axes_d(ax)
gm = []
for i, (gx, gy) in enumerate(goals):
    gm.append(ax.plot(gx, gy, 'o', ms=11, mfc='white', mec='k', mew=1, zorder=4)[0])
    ax.text(gx, gy, str(i + 1), ha='center', va='center', fontsize=7, zorder=5)
trail, = ax.plot([], [], color='tab:blue', lw=1.6, zorder=3)
body = Polygon(L.FP, closed=True, fill=False, ec='tab:blue', lw=1.3, zorder=6); ax.add_patch(body)
fig.tight_layout(); w = L.writer(A.out, A.fps)
with w.saving(fig, A.out, 100):
    # 11-19 §2: 11-19 판은 간격(8 s)이 끝을 건너뛰어 마지막 장('… reached')이 한 번도 안 나왔다 → 끝 시각을 꼭 넣고 1 s 멈춤
    for tf in np.r_[np.arange(t[0], t[-1], A.speed / A.fps), [t[-1]] * A.fps]:
        j = min(np.searchsorted(t, tf), len(t) - 1); last = j == len(t) - 1
        trail.set_data(x[:j + 1], y[:j + 1])
        c, s = math.cos(yaw[j]), math.sin(yaw[j]); body.set_xy(L.FP @ np.array([[c, s], [-s, c]]) + [x[j], y[j]])
        for i, mk in enumerate(gm):
            mk.set_markerfacecolor('tab:green' if (i + 1 < g[j] or last) else 'white')
            mk.set_markeredgecolor('tab:orange' if (i + 1 == g[j] and not last) else 'k')
        # 'goal 8/8' 은 향하는 목표 번호인데 도착 수로 읽힘(11-19 §1) → 문구; 끝 문구는 실제 성공 수로
        ax.set_title(f'{NAME}  {ok} of {NG} goals reached' if last else f'{NAME}  -> goal {g[j]} of {NG}', loc='left')
        ax.set_title(f't = {tf - t[0]:3.0f} s  (x{A.speed:g})', loc='right')
        w.grab_frame()
print('->', A.out)
