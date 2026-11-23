#!/usr/bin/env python3
"""fig_scene — 주행 한 구간의 '로버 주변 장면' 을 GIF · mp4 로(로버를 따라가는 창). 장면 영상 도구 5 개를 하나로 합친 것(2026-11-19 §2).
  왜: 사용자 — "tools 의 도구들이 겹치는 것들이 많을 텐데, 이제 그렇지 않게". fig_run_video · fig_box_approach_video · fig_drive_video · fig_rviz_video ·
      11-19 jobs/fig_readme_scene_1119 가 같은 bag 읽기 · tf 사슬 · 경로 고르기 · 그리기를 따로 복사해 갖고 있었다 → 공통은 lib_rover, 장면은 이것 하나.
  로버 움직임: 없음(bag 읽기만).
  사용: fig_scene.py bag 출력.gif|.mp4 시작HH:MM:SS 끝HH:MM:SS [--speed 2] [--events nav2.log|nav_events.txt] [--title 이름]
          [--frame odom|map] [--style d|light|rviz] [--view 반폭m=1.4] [--fps 5] [--px 560] [--box x0,x1,y0,y1(map)] [--no-mppi]
  출력: 지정한 파일(.gif = Pillow, 그 밖 = ffmpeg) + 표준 출력에 읽은 개수 · 사건 목록.
  frame odom(기본, 11-19 README 판) = 바탕 로컬 코스트맵 · 경로 /transformed_global_plan · MPPI 후보(기록 표본)와 고른 궤적.
  frame map(옛 영상 도구들) = 바탕 전역 코스트맵 · BT 가 준 전역 경로(lib_rover.bt_plans, 바뀐 뒤 3 s 는 직전 경로 점선) · 로컬 치명 칸(□) · 막힘 판정 점(×).
  두 frame 공통 = 라이다 · 카메라 시야 · 차체 · 지나온 길 · 최근 사건(제목 오른쪽, 2.5 s)."""
import argparse, math, sys
from pathlib import Path
import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Wedge
from matplotlib.lines import Line2D
sys.path.insert(0, str(Path(__file__).resolve().parent)); import lib_rover as L

ap = argparse.ArgumentParser()
ap.add_argument('bag'); ap.add_argument('out'); ap.add_argument('start'); ap.add_argument('end')
ap.add_argument('--speed', type=float, default=2.0); ap.add_argument('--events'); ap.add_argument('--title')
ap.add_argument('--frame', choices=('odom', 'map'), default='odom'); ap.add_argument('--style', choices=('d', 'light', 'rviz'), default='d')
ap.add_argument('--view', type=float, default=1.4); ap.add_argument('--fps', type=int, default=5); ap.add_argument('--px', type=int, default=560)
ap.add_argument('--box'); ap.add_argument('--no-mppi', action='store_true')
# 11-23 §7: --seen = '라이다엔 없는데 카메라가 잡은 칸' 표시(사용자: 라이다 스캔에 없던 상자를 카메라가 잡고 계획기가 경로를 고치는 모습).
#   카메라 칸 = 로컬 치명 칸 중 라이다 점이 0.1 m 안에 없는 것(3 m 안). 지금 카메라 시야(±43° · 2.0 m = nvblox 통합 거리) 안 = 채운 칸, 밖 = 빈 칸(기억).
#   시야 부채꼴도 2.0 m 로(기본 1.4 m 는 10-22 전 통합 거리), 전역 경로가 바뀌면 직전 경로를 3 s 점선으로(odom 판에도).
#   --seen x0,x1,y0,y1(지도) 를 주면 그 영역 칸만 표시 — 벽 · 가구도 라이다 평면 밖은 '카메라만' 으로 잡혀 화면이 어지러움(11-23 1 차 렌더).
ap.add_argument('--seen', nargs='?', const='all')
A = ap.parse_args(); MAPF = A.frame == 'map'; RUN = A.title if A.title is not None else Path(A.bag).name.replace('bag_', '')
FOVR = 2.0 if A.seen else L.CAMR; HOLD = 6.0 if A.seen else 3.0   # 직전 경로 점선 유지 시간
SEENR = None if A.seen in (None, 'all') else np.array([float(v) for v in A.seen.split(',')])

# 스타일별 색(D = 11-19 사용자 선택 · light = 10-27 §13 · rviz = 10-26 §17 의 근사)
S = {'d': dict(bg='white', ink='k', plan='tab:green', navfn='tab:green', trail='tab:blue', body='tab:blue', cand='tab:orange', opt='k',
               scan='tab:red', local='tab:purple', fov='tab:olive', ev='tab:red'),
     'light': dict(bg='white', ink='#1b1f24', plan='#0f9d58', navfn='#e8590c', trail='#5b6470', body='#1c7ed6', cand='#f59f00', opt='#1b1f24',
                   scan='#d6336c', local='#e8590c', fov='#f59f00', ev='#b3263e'),
     'rviz': dict(bg='#303030', ink='#e8e8e8', plan='#19ff00', navfn='#19ff00', trail='#ffffff', body='#19ff00', cand='#ffd400', opt='#ffffff',
                  scan='#ff2a2a', local='#ffd400', fov='#f59f00', ev='#ffd400')}[A.style]
L.style_d(); CM = L.costmap_cmap(A.style)

topics = ['/tf', '/scan', '/local_costmap/costmap'] + (['/global_costmap/costmap', '/plan', '/plan_smoothed'] if MAPF else ['/transformed_global_plan'] + (['/plan', '/plan_smoothed'] if A.seen else []))
if not A.no_mppi: topics.append('/trajectories')
D = L.read_bag(A.bag, topics, A.start, A.end); tA, tB = D['tA'], D['tB']
EV, BT, BLK = L.nav_events(A.events, D['day'], tA, tB)
PL = L.bt_plans(D, BT) if (MAPF or A.seen) else []
print('pose', len(D['ob']), 'map->odom', len(D['mo']), 'local', len(D['loc']), 'global', len(D['glo']), 'plan', len(PL) if MAPF else len(D['tplan']),
      'traj', len(D['traj']), 'scan', len(D['scan']), 'static', len(D['static']), 'events', len(EV))
for e in EV: print('  ', L.hms(e[0], 2), e[1])
if MAPF and not D['glo']: sys.exit('전역 코스트맵이 bag 에 없음 — --frame odom 으로')
I4 = np.eye(4)
Mmo = lambda t: L.last(D['mo'], t)[1] if MAPF else I4                # 그리는 프레임 ← odom
def pose(t): return Mmo(t) @ L.last(D['ob'], t)[1]
BOX = np.array([float(v) for v in A.box.split(',')]) if A.box else None

leg = [Line2D([], [], color=S['plan'], lw=1.6, label='global plan'), Line2D([], [], color=S['trail'], lw=1.4, label=A.frame)]
if not A.no_mppi: leg += [Line2D([], [], color=S['cand'], lw=0.9, label='MPPI samples'), Line2D([], [], color=S['opt'], lw=1.6, label='MPPI optimal')]
if MAPF: leg += [Line2D([], [], marker='s', ls='', mfc='none', mec=S['local'], label='local lethal')]
if A.seen: leg += [Line2D([], [], marker='s', ls='', mfc=S['local'], mec=S['local'], label='camera only: in view'),
                   Line2D([], [], marker='s', ls='', mfc='none', mec=S['local'], label='camera only: remembered'),
                   Line2D([], [], color=S['ink'], lw=1.0, ls=(0, (4, 3)), alpha=0.6, label='previous plan')]
leg += [Line2D([], [], color=S['scan'], marker='.', ls='', label='scan')]
if MAPF and A.style == 'light': leg[0] = Line2D([], [], color=S['plan'], lw=1.6, label='plan (Smac)'); leg.insert(1, Line2D([], [], color=S['navfn'], lw=1.6, ls='--', label='plan (NavFn)'))

fig, ax = plt.subplots(figsize=(A.px / 100, A.px / 100), dpi=100, facecolor=S['bg'])
cell_pt = (0.05 * (A.px * 0.8) / (2 * A.view) * 72 / 100 * 0.8) ** 2   # 0.05 m 칸을 화면 점²으로(대략)
trail, prev, cur, chg = [], None, None, -99.0
w = L.writer(A.out, A.fps)
with w.saving(fig, A.out, 100):
    for tf in np.arange(tA, tB, A.speed / A.fps):
        if L.last(D['ob'], tf) is None or (MAPF and not D['mo']): continue
        T = pose(tf); x, y, yaw = L.xyyaw(T); Tmo = Mmo(tf); trail.append((x, y))
        ax.clear(); ax.set_facecolor(S['bg'])
        bg = L.last(D['glo' if MAPF else 'loc'], tf)
        if bg: ax.imshow(L.cm_index(bg[4]), cmap=CM, vmin=0, vmax=101, origin='lower', interpolation='nearest', extent=L.grid_extent(bg))
        if MAPF:
            lc = L.last(D['loc'], tf)
            if lc:
                P = L.w2(Tmo, L.lethal_cells(lc))
                if len(P): ax.scatter(P[:, 0], P[:, 1], s=cell_pt, marker='s', facecolors='none', edgecolors=S['local'], linewidths=0.7, zorder=3)
        cx, cy = x + L.CAMX * math.cos(yaw), y + L.CAMX * math.sin(yaw)
        ax.add_patch(Wedge((cx, cy), FOVR, math.degrees(yaw - L.HFOV), math.degrees(yaw + L.HFOV), fc=S['fov'], ec='none', alpha=0.2 if A.seen else 0.12))
        if A.seen: ax.add_patch(Wedge((cx, cy), FOVR, math.degrees(yaw - L.HFOV), math.degrees(yaw + L.HFOV), fill=False, ec=S['fov'], lw=0.8, alpha=0.7, zorder=3))
        sc = L.last(D['scan'], tf); SP = None
        if sc and tf - sc[0] < 0.5:
            Tl = L.chain(D['static'], sc[1])
            if Tl is not None:
                SP = L.w2(T @ Tl, sc[2]); ax.scatter(SP[:, 0], SP[:, 1], s=3, c=S['scan'], linewidths=0, zorder=4)
        if A.seen:   # 카메라만 잡은 칸 — 라이다 점 0.1 m 안에 없는 로컬 치명 칸(3 m 안)
            lc = L.last(D['loc'], tf)
            if lc:
                P = L.w2(Tmo, L.lethal_cells(lc)); P = P[np.hypot(P[:, 0] - x, P[:, 1] - y) < 3.0] if len(P) else P
                if SEENR is not None and len(P) and D['mo']:   # 지도 영역 안 칸만
                    Q = L.w2(L.last(D['mo'], tf)[1] @ np.linalg.inv(Tmo), P)
                    P = P[(Q[:, 0] >= SEENR[0]) & (Q[:, 0] <= SEENR[1]) & (Q[:, 1] >= SEENR[2]) & (Q[:, 1] <= SEENR[3])]
                if len(P) and SP is not None and len(SP):
                    dmin = np.min(np.hypot(P[:, None, 0] - SP[None, :, 0], P[:, None, 1] - SP[None, :, 1]), axis=1); P = P[dmin > 0.1]
                if len(P):
                    dx, dy = P[:, 0] - cx, P[:, 1] - cy; br = np.abs((np.arctan2(dy, dx) - yaw + math.pi) % (2 * math.pi) - math.pi)
                    inv = (br <= L.HFOV) & (np.hypot(dx, dy) <= FOVR)
                    # 칸 크기 그대로면 상자(2 ~ 4 칸)가 점처럼 안 보여(11-23 1 차) 약 2 배로
                    ax.scatter(P[inv, 0], P[inv, 1], s=cell_pt * 4, marker='s', c=S['local'], edgecolors='white', linewidths=0.6, zorder=6)
                    ax.scatter(P[~inv, 0], P[~inv, 1], s=cell_pt * 4, marker='s', facecolors='white', edgecolors=S['local'], linewidths=1.4, zorder=6)
        if MAPF:   # BT 경로 — 바뀐 뒤 3 s 는 직전 경로를 점선
            p = L.last([q for q in PL if q[0] <= tf], tf)
            if p is not None and (cur is None or p[0] != cur[0]):
                if cur is not None: prev, chg = cur, tf
                cur = p
            if prev is not None and tf - chg < 3.0: ax.plot(prev[1][:, 0], prev[1][:, 1], color=S['ink'], lw=1.0, ls=(0, (4, 3)), alpha=0.5, zorder=3)
            if cur is not None:
                nav = cur[3] == 'NavFn' and A.style == 'light'
                ax.plot(cur[1][:, 0], cur[1][:, 1], color=S['navfn'] if nav else S['plan'], lw=1.6, ls='--' if nav else '-', zorder=3)
        else:
            if A.seen and D['mo']:   # 전역 경로 전체(지도 → odom) — 잘린 /transformed_global_plan 은 상자까지 안 닿아 '상자를 지나던 경로' 가 안 보임(11-23)
                Mom = np.linalg.inv(L.last(D['mo'], tf)[1])
                p = L.last([q for q in PL if q[0] <= tf], tf)
                if p is not None and (cur is None or p[0] != cur[0]):
                    if cur is not None: prev, chg = cur, tf
                    cur = p
                if prev is not None and tf - chg < HOLD:   # 바뀐 뒤 HOLD 초는 직전 경로를 점선
                    P = L.w2(Mom, prev[1]); ax.plot(P[:, 0], P[:, 1], color=S['ink'], lw=1.0, ls=(0, (4, 3)), alpha=0.6, zorder=3)
                if cur is not None:
                    P = L.w2(Mom, cur[1]); ax.plot(P[:, 0], P[:, 1], color=S['plan'], lw=1.6, zorder=3)
            else:
                pl = L.last(D['tplan'], tf)
                if pl is not None and len(pl[1]): ax.plot(pl[1][:, 0], pl[1][:, 1], color=S['plan'], lw=1.6, zorder=3)
        tr_ = np.array(trail); ax.plot(tr_[:, 0], tr_[:, 1], color=S['trail'], lw=1.4, zorder=3)
        ax.add_patch(Polygon(L.w2(T, L.FP), closed=True, fill=False, ec=S['body'], lw=1.2, zorder=5))
        tj = L.last(D['traj'], tf)
        if tj and tf - tj[0] < 0.5:   # /trajectories 는 odom 프레임
            for k in tj[1]: P = L.w2(Tmo, k); ax.plot(P[:, 0], P[:, 1], color=S['cand'], lw=0.9, alpha=0.9, zorder=6)
            if len(tj[2]): P = L.w2(Tmo, tj[2]); ax.plot(P[:, 0], P[:, 1], color=S['opt'], lw=1.6, zorder=7)
        bk = [q for q in BLK if tf - 2.5 <= q[0] <= tf]
        if bk:   # 막힘 판정 점은 map 좌표
            P = L.w2(np.linalg.inv(L.last(D['mo'], tf)[1]), [bk[-1][1:]]) if not MAPF and D['mo'] else (np.array([bk[-1][1:]]) if MAPF else None)
            if P is not None: ax.plot(P[:, 0], P[:, 1], 'x', color=S['ev'], ms=9, mew=2, zorder=8)
        if BOX is not None:
            P = np.array([[BOX[0], BOX[2]], [BOX[1], BOX[2]], [BOX[1], BOX[3]], [BOX[0], BOX[3]]])
            if not MAPF: P = L.w2(np.linalg.inv(L.last(D['mo'], tf)[1]), P) if D['mo'] else None
            if P is not None: ax.add_patch(Polygon(P, closed=True, fill=False, ec=S['ink'], ls='--', lw=1.0, zorder=6))
        ax.set_xlim(x - A.view, x + A.view); ax.set_ylim(y - A.view, y + A.view)
        L.axes_d(ax, f'{A.frame} x (m)', f'{A.frame} y (m)')
        if A.style == 'rviz':
            ax.tick_params(colors=S['ink']); ax.xaxis.label.set_color(S['ink']); ax.yaxis.label.set_color(S['ink'])
            for s_ in ax.spines.values(): s_.set_color('#a0a0a4')
        ax.legend(handles=leg, loc='lower left', fontsize=7)
        e = max((e for e in EV if e[0] <= tf and tf - e[0] < 2.5), key=lambda e: e[0], default=None)
        ax.set_title(f'{RUN}  {L.hms(tf)}  (x{A.speed:g})', loc='left', color=S['ink'])
        ax.set_title(e[1] if e else '', loc='right', color=S['ev'])
        fig.tight_layout(); w.grab_frame()
print('->', A.out)
