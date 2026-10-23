#!/usr/bin/env python3
"""fig_mppi_stop — f2pa2 5.5 s 정지를 한 장으로(2026-10-23 §8, PC, 로버 안 움직임).
  위 3 칸(정지 전 · 정지 중 · 다시 출발, odom 좌표, 로버 둘레 확대):
    바탕 = 로컬 코스트맵(빨강 치명 · 주황 내접 · 옅은 노랑 팽창), 초록 사각 = 차체, 보라 선 = 컨트롤러가 받은 경로, 보라 별 = 목표 W3(화살표 = 목표 방향),
    회색 점 = MPPI 후보 궤적(lite 표본), 원 = MPPI 최적 궤적 32 단계(색 = 그 단계 속도, 파랑 느림 → 노랑 빠름), 굵은 원 = 첫 단계(= 실제 명령).
    점선 화살표 = 0.3 m 앞 경로 방향, 실선 화살표 = 목표 방향(GoalCritic 1.0 m 안에서 켜짐).
  아래 왼쪽: 세 시각의 최적 궤적 단계 속도. 아래 오른쪽: 시간에 따른 명령 v · 경로 방향과 목표 방위의 엇갈림(°).
  인자: bag 출력.png 목표x,y,yaw° 시각들(정지 전,정지 중,출발) 그래프 시작s 끝s"""
import sys, math, bisect
from pathlib import Path
import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, FancyArrow
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
plt.rcParams['font.family'] = 'Malgun Gothic'; plt.rcParams['axes.unicode_minus'] = False
bag, out = sys.argv[1], sys.argv[2]; GX, GY, GYAW = (float(v) for v in sys.argv[3].split(',')); GYAW = math.radians(GYAW)
TS = [float(v) for v in sys.argv[4].split(',')]; GA, GB = float(sys.argv[5]), float(sys.argv[6])
FP = np.array([[0.262, 0.165], [0.262, -0.165], [-0.248, -0.165], [-0.248, 0.165]])
yq = lambda q: math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z)); wrap = lambda a: math.atan2(math.sin(a), math.cos(a))
MO, OB, TR, TP, CMD, LC = [], [], [], [], [], []
with AnyReader([Path(bag)], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
    T0 = rd.start_time * 1e-9
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/tf', '/trajectories', '/transformed_global_plan', '/cmd_vel', '/local_costmap/costmap')]):
        tt = t * 1e-9 - T0
        if c.topic != '/tf' and not (min(GA, min(TS)) - 2 <= tt <= max(GB, max(TS)) + 1): continue
        m = rd.deserialize(raw, c.msgtype)
        if c.topic == '/tf':
            for tr in m.transforms:
                v = (tr.transform.translation.x, tr.transform.translation.y, yq(tr.transform.rotation))
                if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom': MO.append((tt, v))
                elif tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link': OB.append((tt, v))
        elif c.topic == '/trajectories':
            opt = np.array([[mk.pose.position.x, mk.pose.position.y] for mk in sorted([mk for mk in m.markers if mk.ns == 'Optimal Trajectory'], key=lambda q: q.id)])
            cand = np.array([[mk.pose.position.x, mk.pose.position.y] for mk in m.markers if mk.ns == 'Candidate Trajectories'])
            TR.append((tt, opt, cand))
        elif c.topic == '/transformed_global_plan': TP.append((tt, np.array([[p.pose.position.x, p.pose.position.y] for p in m.poses]) if m.poses else np.zeros((0, 2))))
        elif c.topic == '/cmd_vel': CMD.append((tt, m.linear.x))
        else:
            g = m.info; LC.append((tt, g.origin.position.x, g.origin.position.y, g.resolution, np.array(m.data, np.int16).reshape(g.height, g.width)))
for L in (MO, OB): L.sort(key=lambda q: q[0])
tl = lambda L: [q[0] for q in L]; MOt, OBt, TRt, TPt, LCt = tl(MO), tl(OB), tl(TR), tl(TP), tl(LC)
last = lambda L, Lt, t: L[max(bisect.bisect_right(Lt, t) - 1, 0)]
def goal_odom(t):
    mo = last(MO, MOt, t)[1]; c, s = math.cos(-mo[2]), math.sin(-mo[2]); dx, dy = GX - mo[0], GY - mo[1]; return (c * dx - s * dy, s * dx + c * dy, GYAW - mo[2])
def angles(t):
    p = last(OB, OBt, t)[1]; Q = last(TP, TPt, t)[1]; g = goal_odom(t)
    if len(Q) < 3: return np.nan, np.nan, np.nan
    i = int(np.argmin(np.linalg.norm(Q - np.array(p[:2]), axis=1))); sacc = np.r_[0, np.cumsum(np.linalg.norm(np.diff(Q[i:], axis=0), axis=1))]; j = min(i + int(np.searchsorted(sacc, 0.3)), len(Q) - 1)
    ph = wrap(math.atan2(Q[j][1] - Q[i][1], Q[j][0] - Q[i][0]) - p[2]) if j > i else np.nan
    gb = wrap(math.atan2(g[1] - p[1], g[0] - p[0]) - p[2]); gd = math.hypot(g[0] - p[0], g[1] - p[1])
    return math.degrees(ph), math.degrees(gb), gd
fig = plt.figure(figsize=(15, 10), facecolor='white'); gs = fig.add_gridspec(2, 3, height_ratios=[1.25, 1])
cmap = plt.get_cmap('viridis'); labels = ('정지 직전', '정지 중', '다시 출발')
for k, t in enumerate(TS):
    ax = fig.add_subplot(gs[0, k]); p = last(OB, OBt, t)[1]
    _, ox, oy, r, A = last(LC, LCt, t); ys, xs = np.nonzero(A > 0); px, py = ox + (xs + .5) * r, oy + (ys + .5) * r; v = A[ys, xs]
    for lo, hi, col in ((1, 50, (0.98, 0.93, 0.65)), (50, 99, (0.97, 0.78, 0.45)), (99, 100, (1, 0.55, 0.15)), (100, 101, (0.85, 0.1, 0.1))):
        kk = (v >= lo) & (v < hi); ax.scatter(px[kk], py[kk], s=30, c=[col], marker='s', lw=0)
    tt, opt, cand = last(TR, TRt, t)
    if len(cand): ax.scatter(cand[:, 0], cand[:, 1], s=3, c='#9e9e9e', lw=0)
    Q = last(TP, TPt, t)[1]
    if len(Q): ax.plot(Q[:, 0], Q[:, 1], color='#7b1fa2', lw=2, label='컨트롤러 경로')
    if len(opt) > 1:
        sp = np.r_[np.linalg.norm(np.diff(opt, axis=0), axis=1) / 0.1, np.nan]; ax.scatter(opt[:-1, 0], opt[:-1, 1], s=26, c=sp[:-1], cmap=cmap, vmin=0, vmax=0.085, edgecolors='k', linewidths=0.3, zorder=5)
        ax.scatter(opt[:1, 0], opt[:1, 1], s=110, facecolors='none', edgecolors='k', linewidths=1.8, zorder=6)
    c_, s_ = math.cos(p[2]), math.sin(p[2]); ax.add_patch(Polygon(np.c_[p[0] + c_ * FP[:, 0] - s_ * FP[:, 1], p[1] + s_ * FP[:, 0] + c_ * FP[:, 1]], closed=True, fc=(0.26, 0.63, 0.28, 0.35), ec='#1b5e20', lw=1.4))
    g = goal_odom(t); ax.plot(g[0], g[1], marker='*', ms=16, color='#6a1b9a'); ax.add_patch(FancyArrow(g[0], g[1], 0.25 * math.cos(g[2]), 0.25 * math.sin(g[2]), width=0.01, color='#6a1b9a'))
    ph, gb, gd = angles(t)
    if not np.isnan(ph): ax.add_patch(FancyArrow(p[0], p[1], 0.45 * math.cos(p[2] + math.radians(ph)), 0.45 * math.sin(p[2] + math.radians(ph)), width=0.008, color='#7b1fa2', ls='--', fill=False, lw=1.5))
    ax.add_patch(FancyArrow(p[0], p[1], 0.45 * math.cos(p[2] + math.radians(gb)), 0.45 * math.sin(p[2] + math.radians(gb)), width=0.008, color='#00897b'))
    ax.set_xlim(p[0] - 0.75, p[0] + 1.05); ax.set_ylim(p[1] - 0.9, p[1] + 0.9); ax.set_aspect('equal'); ax.grid(alpha=0.25); ax.tick_params(labelsize=7)
    cv = last(CMD, tl(CMD), t)[1]
    ax.set_title('%s  t %.1f s\n명령 v %.3f m/s · 경로 방향 %+.0f° · 목표 방위 %+.0f° (엇갈림 %.0f°) · 목표 %.2f m' % (labels[k], t, cv, ph, gb, abs(ph - gb), gd), fontsize=9)
    if k == 0: ax.legend(fontsize=7, loc='lower left')
axS = fig.add_subplot(gs[1, 0])
for k, t in enumerate(TS):
    tt, opt, cand = last(TR, TRt, t)
    if len(opt) > 1: axS.plot(np.arange(1, len(opt)) * 0.1, np.linalg.norm(np.diff(opt, axis=0), axis=1) / 0.1, marker='o', ms=3, label='%s t %.1f' % (labels[k], t))
axS.set_xlabel('최적 궤적 단계 시각(s, 0 = 지금)'); axS.set_ylabel('단계 속도 m/s'); axS.set_ylim(0, 0.1); axS.grid(alpha=0.3); axS.legend(fontsize=8)
axS.set_title('정지 중엔 처음 0.4 s 가 거의 0 — 실제 명령은 첫 단계', fontsize=9)
axT = fig.add_subplot(gs[1, 1:]); TT = np.arange(GA, GB, 0.2); AN = np.array([angles(t) for t in TT])
cv = np.array([q for q in CMD if GA <= q[0] <= GB]); axT.plot(cv[:, 0], cv[:, 1], color='#1565c0', lw=1.2, label='명령 v (m/s)')
axT.set_ylabel('명령 v m/s', color='#1565c0'); axT.set_ylim(-0.01, 0.1); axT.set_xlabel('bag 시각 t (s)'); axT.grid(alpha=0.3)
ax2 = axT.twinx(); ax2.plot(TT, AN[:, 0], color='#7b1fa2', lw=1, label='경로 방향(°)'); ax2.plot(TT, AN[:, 1], color='#00897b', lw=1, label='목표 방위(°)')
ax2.plot(TT, np.abs(AN[:, 0] - AN[:, 1]), color='#d32f2f', lw=1.6, label='엇갈림(°)'); ax2.set_ylabel('°'); ax2.set_ylim(-60, 80)
gon = TT[AN[:, 2] < 1.0]
if len(gon): axT.axvspan(gon[0], TT[-1], color='#00897b', alpha=0.06)
for t in TS: axT.axvline(t, color='#555', lw=0.7, ls=':')
h1, l1 = axT.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels(); axT.legend(h1 + h2, l1 + l2, fontsize=8, loc='upper right')
axT.set_title('명령과 방향 엇갈림 — 옅은 청록 = 목표 1 m 안(GoalCritic 켜짐), 점선 = 위 세 장면', fontsize=9)
fig.suptitle('f2pa2 W3 앞 5.5 s 정지 — 경로(보라, 오른쪽으로 꺾임)와 목표(청록, 왼쪽)가 엇갈린 자리에서 MPPI 가 "0.4 s 뒤 출발" 해에 갇힘 (PathAlign 28)', fontsize=11)
plt.tight_layout(rect=(0, 0, 1, 0.96)); plt.savefig(out, dpi=120); print('그림', out)
