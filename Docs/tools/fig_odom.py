#!/usr/bin/env python3
"""fig_odom — 오도메트리 · 위치 추정 · 속도 추종을 GIF · mp4 로(스타일 D). 11-19 jobs/fig_readme_odom_1119 를 lib_rover 로 옮긴 상시판(2026-11-19 §2).
  왜: README '펌웨어 · 센서 융합 · 위치 추정' 그림을 다시 만들 수 있게, 그리고 bag 읽기 · 지도 · 좌표 변환을 lib_rover 하나로(도구 겹침 정리).
  모드: fusion = 휠만 · EKF · 지도 위치(map→odom ∘ EKF) 경로를 출발 자세만 맞춰 겹침, 제목 오른쪽 = 그 순간 지도 위치와의 거리
        loc    = 같은 라이다 스캔을 EKF 만(첫 map→odom 고정) / slam_toolbox(그때 map→odom)로 저장 지도에 얹은 두 판
        fw     = /cmd_vel 지령 vs /wheel_odom 속도(v · ω), 20 s 창이 흐름
  로버 움직임: 없음. 입력: bag(/tf · /wheel_odom · /odometry/filtered · /cmd_vel · /scan), 저장 지도 --map(기본 office_v3).
  사용: fig_odom.py fusion|loc|fw bag 출력.gif [--speed 40] [--title 이름] [--map office_v3] [--from 0 --to 60(fw, bag 시작 기준 초)] [--fps 5]
  출력: 지정 파일 + 표준 출력에 읽은 개수, fusion 은 끝 · 최대 거리(휠만 · EKF)."""
import argparse, math, sys
from pathlib import Path
import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
sys.path.insert(0, str(Path(__file__).resolve().parent)); import lib_rover as L

ap = argparse.ArgumentParser()
ap.add_argument('mode', choices=('fusion', 'loc', 'fw')); ap.add_argument('bag'); ap.add_argument('out')
ap.add_argument('--speed', type=float, default=40.0); ap.add_argument('--title'); ap.add_argument('--map', default='office_v3')
ap.add_argument('--from', dest='a0', type=float, default=0.0); ap.add_argument('--to', dest='a1', type=float, default=60.0); ap.add_argument('--fps', type=int, default=5)
A = ap.parse_args(); RUN = A.title or Path(A.bag).name.replace('bag_', ''); L.style_d()
D = L.read_bag(A.bag, ['/tf', '/wheel_odom', '/odometry/filtered', '/cmd_vel'] + (['/scan'] if A.mode == 'loc' else []), scan_max=8.0)
t0 = D['t0']; rel = lambda seq: [(s[0] - t0,) + tuple(s[1:]) for s in seq]   # bag 시작 기준 초
mo, wo, ek, cmd, scan = rel(D['mo']), rel(D['wheel']), rel(D['ekf']), rel(D['cmd']), rel(D['scan'])
print('map->odom', len(mo), 'wheel', len(wo), 'ekf', len(ek), 'cmd', len(cmd), 'scan', len(scan))
xy = lambda M: np.array(L.xyyaw(M)[:2])
tE = min(ek[-1][0], wo[-1][0], mo[-1][0]) if A.mode != 'fw' else A.a1; w = L.writer(A.out, A.fps)

if A.mode == 'fusion':
    Tmo0, E0, W0 = mo[0][1], ek[0][1], wo[0][1]
    P_w = np.array([xy(Tmo0 @ E0 @ np.linalg.inv(W0) @ s[1]) for s in wo]); P_e = np.array([xy(Tmo0 @ s[1]) for s in ek])
    P_m = np.array([xy(L.last(mo, s[0])[1] @ s[1]) for s in ek])
    tw = np.array([s[0] for s in wo]); te = np.array([s[0] for s in ek])
    dw = np.hypot(*(P_w[np.clip(np.searchsorted(tw, te), 0, len(P_w) - 1)] - P_m).T); de = np.hypot(*(P_e - P_m).T)
    print('end  wheel %.2f m  EKF %.2f m   max  wheel %.2f m  EKF %.2f m  (%.1f s)' % (dw[-1], de[-1], dw.max(), de.max(), tE))
    fig, ax = plt.subplots(figsize=(6.4, 5.6), dpi=100); L.draw_map(ax, A.map); L.axes_d(ax)
    allp = np.r_[P_w, P_m]; ax.set_xlim(allp[:, 0].min() - 0.5, allp[:, 0].max() + 0.5); ax.set_ylim(allp[:, 1].min() - 0.5, allp[:, 1].max() + 0.5)
    lw_, = ax.plot([], [], color='tab:orange', lw=1.6, label='wheel odometry')
    le, = ax.plot([], [], color='tab:blue', lw=1.6, label='EKF')
    lm, = ax.plot([], [], color='k', lw=1.2, ls='--', label='map (slam_toolbox)')
    ax.legend(loc='lower left', fontsize=7.5); ax.set_title(RUN, loc='left'); ax.set_title('wheel', loc='right'); fig.tight_layout()   # 제목을 먼저 넣고 맞춰야 위가 안 잘림(11-19 §1)
    with w.saving(fig, A.out, 100):
        for ts in np.arange(0, tE + 2, A.speed / A.fps):
            i = np.searchsorted(tw, ts); j = np.searchsorted(te, ts)
            lw_.set_data(P_w[:i, 0], P_w[:i, 1]); le.set_data(P_e[:j, 0], P_e[:j, 1]); lm.set_data(P_m[:j, 0], P_m[:j, 1])
            k = min(j, len(P_m) - 1); kw = min(i, len(P_w) - 1)
            ax.set_title(f'{RUN}  t = {min(ts, tE):3.0f} s  (x{A.speed:g})', loc='left')
            ax.set_title(f'wheel {np.hypot(*(P_w[kw] - P_m[k])):.2f} m   EKF {np.hypot(*(P_e[k] - P_m[k])):.2f} m', loc='right')
            w.grab_frame()
elif A.mode == 'loc':
    Tmo0 = mo[0][1]; VIEW = 2.2
    fig, axs = plt.subplots(1, 2, figsize=(9.0, 4.9), dpi=100)
    for ax in axs: L.draw_map(ax, A.map); L.axes_d(ax)
    axs[0].set_title('EKF only', loc='left'); axs[1].set_title('slam_toolbox', loc='left')
    arts = []; fig.tight_layout()
    with w.saving(fig, A.out, 100):
        for ts in np.arange(1, tE, A.speed / A.fps):
            for a_ in arts: a_.remove()
            arts = []
            sc = L.last(scan, ts); Tob = L.last(ek, ts)[1]; Tl = L.chain(D['static'], sc[1])
            for ax, Tm in ((axs[0], Tmo0), (axs[1], L.last(mo, ts)[1])):
                P = L.w2(Tm @ Tob @ Tl, sc[2]); x, y, _ = L.xyyaw(Tm @ Tob)
                arts.append(ax.scatter(P[:, 0], P[:, 1], s=3, c='tab:red', linewidths=0, zorder=5))
                arts.append(ax.add_patch(Polygon(L.w2(Tm @ Tob, L.FP), closed=True, fill=False, ec='tab:blue', lw=1.2, zorder=6)))
                ax.set_xlim(x - VIEW, x + VIEW); ax.set_ylim(y - VIEW * 0.8, y + VIEW * 0.8)
            d = np.hypot(*(xy(Tmo0 @ Tob) - xy(L.last(mo, ts)[1] @ Tob)))
            axs[1].set_title(f't = {ts:3.0f} s (x{A.speed:g})   offset {d:.2f} m', loc='right')
            w.grab_frame()
else:
    WIN = 20.0; C = np.array(cmd); Wt = np.array([(s[0], s[2], s[3]) for s in wo])
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(6.4, 4.4), dpi=100, sharex=True)
    with w.saving(fig, A.out, 100):
        for ts in np.arange(A.a0 + WIN * 0.5, A.a1, A.speed / A.fps):
            for ax, k, lab, lim in ((ax1, 1, 'v (m/s)', (-0.02, 0.11)), (ax2, 2, 'ω (rad/s)', (-0.5, 0.5))):
                ax.clear(); s0 = ts - WIN
                mc = (C[:, 0] >= s0) & (C[:, 0] <= ts); mw = (Wt[:, 0] >= s0) & (Wt[:, 0] <= ts)
                ax.step(C[mc, 0], C[mc, k], where='post', color='tab:blue', lw=1.4, label='/cmd_vel')
                ax.plot(Wt[mw, 0], Wt[mw, k], color='tab:orange', lw=1.2, label='/wheel_odom')
                ax.set_xlim(s0, ts); ax.set_ylim(*lim); ax.set_ylabel(lab); ax.grid(alpha=0.3)
            ax1.legend(loc='lower left', fontsize=7.5, ncol=2); ax2.set_xlabel('t (s)')
            ax1.set_title(f'{RUN}  (x{A.speed:g})', loc='left'); fig.tight_layout(); w.grab_frame()
print('->', A.out)
