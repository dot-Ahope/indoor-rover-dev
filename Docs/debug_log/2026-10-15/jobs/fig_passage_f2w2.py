#!/usr/bin/env python3
"""fig_passage_f2w2 — 마지막 주행 f2w2(no5, ClearanceBandCritic 켬)의 서쪽 통로 남행 구간: 움직임 · 장애물 · 명령 · 놓침 한 장. (2026-10-15 §33, 오늘만)
  왜: 사용자 "가장 마지막 bag의 해당 통로에서 움직임 및 장애물 시각화해달라." (§32 상자 쪽으로 몸 튼 두 자리 포함)
  그림: (가) 위에서 본 통로 — 저장 지도(회색), 로컬 코스트맵 치명 칸을 라이다 확인(남색) / 카메라만(주황)으로, 진할수록 오래 찍힘,
        차체 윤곽 1 s 마다(시간 색), 중심 궤적, 목표 4 경로, 몸 튼 두 자리 A · B, 재계획 정지 자리.
        (나)(다) A · B 순간 확대 — 그 순간 로컬 코스트맵(팽창 회색 농도, 치명 칸 라이다/카메라), 차체, MPPI 후보 궤적 점(회색) · 최적 궤적(빨강) · 따라가는 경로(초록).
        (라) 시간축 — 지도 여유(뒤집힘 구간 2.7~4.4 cm · 크리틱 띠 6 cm), 명령 ω, 초당 제어 주기 놓침(10 = 전부).
  라이다 확인 = 그 칸 중심 4 cm 안에 ±0.3 s 라이다 점이 있음. 인자: bag 놓침파일 그림경로"""
import sys, time, math, re
from pathlib import Path
import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection

bag, missf, out = sys.argv[1:4]
T0s, T1s = '17:36:04', '17:36:46'; A_s, B_s, STOP_s = '17:36:11.5', '17:36:31.0', '17:36:18.5'
PAD = (0.272, -0.258, 0.175)
yq = lambda q: math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
compose = lambda A, B: (A[0] + math.cos(A[2]) * B[0] - math.sin(A[2]) * B[1], A[1] + math.sin(A[2]) * B[0] + math.cos(A[2]) * B[1], A[2] + B[2])


def qm(q):
    x, y, z, w = q.x, q.y, q.z, q.w
    return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)], [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)], [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])


def tsec(day, h):
    hm, _, fr = h.partition('.'); return time.mktime(time.strptime(day + hm, '%Y-%m-%d %H:%M:%S')) + (float('0.' + fr) if fr else 0)


def foot(P):
    c, s = math.cos(P[2]), math.sin(P[2]); f, r, h = PAD
    return [(P[0] + c * a - s * b, P[1] + s * a + c * b) for a, b in ((f, h), (f, -h), (r, -h), (r, h))]


static = {}; mo = ob = None; MAP = None; poses = []; scans = []; grids = []; trajs = []; tplans = []; plans = []; cmds = []; day = None
with AnyReader([Path(bag)], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/tf', '/tf_static', '/map', '/scan', '/local_costmap/costmap', '/trajectories', '/transformed_global_plan', '/plan', '/cmd_vel')]):
        ts = t / 1e9
        if day is None: day = time.strftime('%Y-%m-%d ', time.localtime(ts)); T0, T1 = tsec(day, T0s) - 2, tsec(day, T1s) + 1
        m = rd.deserialize(raw, c.msgtype)
        if c.topic == '/tf_static':
            for tr in m.transforms: static[tr.child_frame_id] = (tr.header.frame_id, np.array([tr.transform.translation.x, tr.transform.translation.y, tr.transform.translation.z]), qm(tr.transform.rotation))
            continue
        if c.topic == '/map':
            if MAP is None: MAP = (np.array(m.data, np.int16).reshape(m.info.height, m.info.width), m.info.origin.position.x, m.info.origin.position.y, m.info.resolution)
            continue
        if c.topic == '/tf':
            for tr in m.transforms:
                v = (tr.transform.translation.x, tr.transform.translation.y, yq(tr.transform.rotation))
                if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom': mo = v
                elif tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link':
                    ob = v
                    if mo is not None and T0 <= ts <= T1: poses.append((ts, mo, ob))
            continue
        if ts < T0 or ts > T1 or mo is None or ob is None: continue
        if c.topic == '/scan': scans.append((ts, m, ob, mo))
        elif c.topic == '/local_costmap/costmap': grids.append((ts, np.array(m.data, np.int16).reshape(m.info.height, m.info.width), (m.info.origin.position.x, m.info.origin.position.y, m.info.resolution), mo, ob))
        elif c.topic == '/trajectories':
            cand = np.array([(mk.pose.position.x, mk.pose.position.y) for mk in m.markers if mk.ns == 'Candidate Trajectories'])
            opt = sorted([mk for mk in m.markers if mk.ns == 'Optimal Trajectory'], key=lambda mk: mk.id)
            trajs.append((ts, cand, np.array([(mk.pose.position.x, mk.pose.position.y) for mk in opt]), mo))
        elif c.topic == '/transformed_global_plan': tplans.append((ts, np.array([(p.pose.position.x, p.pose.position.y) for p in m.poses]), mo))
        elif c.topic == '/plan': plans.append((ts, np.array([(p.pose.position.x, p.pose.position.y) for p in m.poses])))
        elif c.topic == '/cmd_vel': cmds.append((ts, m.linear.x, m.angular.z))
T0, T1, TA, TB, TS = tsec(day, T0s), tsec(day, T1s), tsec(day, A_s), tsec(day, B_s), tsec(day, STOP_s)


def to_map(M, x, y):
    return M[0] + np.cos(M[2]) * x - np.sin(M[2]) * y, M[1] + np.sin(M[2]) * x + np.cos(M[2]) * y


# base_link → lidar 프레임(3D, 라이다는 뒤집혀 장착)
def chain(frame):
    R, T = np.eye(3), np.zeros(3)
    while frame != 'base_link':
        p, t, r = static[frame]; R, T = r @ R, r @ T + t; frame = p
    return R, T
RL, TLd = chain(scans[0][1].header.frame_id)


def scan_odom(sc):
    _, m, obp, _ = sc; r = np.array(m.ranges); an = m.angle_min + np.arange(len(r)) * m.angle_increment; ok = np.isfinite(r) & (r > m.range_min) & (r < 3.0)
    p = np.stack([r[ok] * np.cos(an[ok]), r[ok] * np.sin(an[ok]), np.zeros(ok.sum())], 1) @ RL.T + TLd
    c, s = math.cos(obp[2]), math.sin(obp[2]); return obp[0] + c * p[:, 0] - s * p[:, 1], obp[1] + s * p[:, 0] + c * p[:, 1]


ST = np.array([s[0] for s in scans])


def cells(g):
    ts, a, (ox, oy, r), M, obp = g; iy, ix = np.nonzero(a >= 100); wx = ox + (ix + 0.5) * r; wy = oy + (iy + 0.5) * r
    k = np.nonzero(np.abs(ST - ts) <= 0.3)[0]; lid = np.zeros(len(wx), bool)
    if len(k):
        sx = np.concatenate([scan_odom(scans[i])[0] for i in k]); sy = np.concatenate([scan_odom(scans[i])[1] for i in k])
        for j in range(len(wx)): lid[j] = (np.hypot(sx - wx[j], sy - wy[j]) < 0.04).any()
    mx, my = to_map(M, wx, wy); return mx, my, lid


plt.rcParams['font.family'] = ['Malgun Gothic', 'DejaVu Sans']; plt.rcParams['axes.unicode_minus'] = False
fig = plt.figure(figsize=(17, 11.5)); gsp = fig.add_gridspec(3, 3, width_ratios=[1.25, 1, 1], height_ratios=[1.15, 0.55, 0.55], wspace=0.22, hspace=0.32)
ax = fig.add_subplot(gsp[:, 0]); axA = fig.add_subplot(gsp[0, 1]); axB = fig.add_subplot(gsp[0, 2])
axC = fig.add_subplot(gsp[1, 1:]); axW = fig.add_subplot(gsp[2, 1:], sharex=axC)
XL, YL = (-2.35, -0.95), (-5.65, -2.45)

# (가) 저장 지도
a, ox, oy, r = MAP; iy, ix = np.nonzero(a >= 65); wx = ox + (ix + 0.5) * r; wy = oy + (iy + 0.5) * r; k = (wx > XL[0] - 0.2) & (wx < XL[1] + 0.2) & (wy > YL[0] - 0.2) & (wy < YL[1] + 0.2)
ax.scatter(wx[k], wy[k], s=14, marker='s', c='#c9cdd2', linewidths=0, label='저장 지도 벽(office_v3)', zorder=1)
# 치명 칸 누적(라이다 / 카메라)
acc = {}
seg = [g for g in grids if T0 <= g[0] <= T1]
for g in seg:
    mx, my, lid = cells(g)
    for x, y, l in zip(mx, my, lid):
        key = (round(x / 0.05) * 0.05, round(y / 0.05) * 0.05); v = acc.setdefault(key, [0, 0]); v[0] += 1; v[1] += l
for (x, y), (n, nl) in acc.items():
    if not (XL[0] < x < XL[1] and YL[0] < y < YL[1]): continue
    frac = n / len(seg); lidar = nl / n >= 0.5
    ax.add_patch(plt.Rectangle((x - 0.025, y - 0.025), 0.05, 0.05, fc=('#2b3a67' if lidar else '#e8730c'), alpha=0.15 + 0.75 * min(frac * 1.5, 1), ec='none', zorder=2))
ax.add_patch(plt.Rectangle((0, 0), 0, 0, fc='#2b3a67', label='치명 칸 · 라이다 확인'))
ax.add_patch(plt.Rectangle((0, 0), 0, 0, fc='#e8730c', label='치명 칸 · 카메라만(라이다 아래)'))
# 경로(목표 4 첫 계획)
p4 = [p for p in plans if tsec(day, '17:36:16.0') <= p[0] <= tsec(day, '17:36:20.0') and len(p[1])]
if p4:
    pl = max(p4, key=lambda q: len(q[1]))   # 목표 4 시작 직후 가장 긴(= 끝까지 이어진) 계획
    ax.plot(pl[1][:, 0], pl[1][:, 1], color='#2e7d32', lw=1.6, ls='--', label='목표 4 계획 경로(%s)' % time.strftime('%H:%M:%S', time.localtime(pl[0])), zorder=3)
# 차체 1 s 마다 + 중심 궤적
PM = [(ts, compose(M, O)) for ts, M, O in poses if T0 <= ts <= T1]
cm = plt.get_cmap('viridis'); last = -9
for ts, P in PM:
    if ts - last >= 1.0:
        last = ts; col = cm((ts - T0) / (T1 - T0)); ax.add_patch(Polygon(foot(P), closed=True, fill=False, ec=col, lw=1.0, alpha=0.9, zorder=4))
C = np.array([P[:2] for _, P in PM]); tt = np.array([ts for ts, _ in PM])
sc = ax.scatter(C[:, 0], C[:, 1], c=tt - T0, cmap='viridis', s=4, zorder=5)
cb = fig.colorbar(sc, ax=ax, orientation='horizontal', fraction=0.03, pad=0.05); cb.set_label('시간 (s, %s 부터)' % T0s)
for lab, T, dx in (('A 입구: 왼쪽(동쪽)으로 틂', TA, -0.55), ('B 상자 끝: 왼쪽으로 틂', TB, -0.62), ('재계획 정지', TS, -0.55)):
    j = int(np.argmin(np.abs(tt - T))); P = PM[j][1]
    ax.add_patch(Polygon(foot(P), closed=True, fill=False, ec='#c62828', lw=2.0, zorder=6))
    ax.annotate(lab, (P[0], P[1]), (XL[0] + 0.02, P[1] + 0.02), fontsize=9, color='#c62828', zorder=7, bbox=dict(fc='white', ec='none', alpha=0.85, pad=1), arrowprops=dict(arrowstyle='-', color='#c62828', lw=0.8))
ax.set_xlim(*XL); ax.set_ylim(*YL); ax.set_aspect('equal'); ax.grid(alpha=0.25)
ax.set_xlabel('지도 x (m)'); ax.set_ylabel('지도 y (m) — 아래가 남쪽, 로버는 위에서 아래로'); ax.legend(loc='lower left', fontsize=8, framealpha=0.9)
ax.set_title('(가) 서쪽 통로 남행 %s~%s · 차체 1 s 마다' % (T0s, T1s), fontsize=11)


# (나)(다) 순간 확대
def zoom(axz, T, title):
    g = min(seg, key=lambda q: abs(q[0] - T)); ts, a, (ox_, oy_, r_), M, obp = g
    P = compose(M, obp)

    def squares(ix, iy):
        # odom 격자 칸 4 꼭짓점 → 지도 좌표 다각형(실제 5 cm 크기, map→odom 회전 반영)
        x0 = ox_ + ix * r_; y0 = oy_ + iy * r_
        cx = np.stack([x0, x0 + r_, x0 + r_, x0], 1); cy = np.stack([y0, y0, y0 + r_, y0 + r_], 1)
        mx, my = to_map(M, cx, cy); return [np.stack([mx[i], my[i]], 1) for i in range(len(ix))]
    iy, ix = np.nonzero((a >= 50) & (a < 100)); v = a[iy, ix]
    pc = PatchCollection([Polygon(q) for q in squares(ix, iy)], facecolor=[plt.get_cmap('Greys')(0.12 + 0.35 * (vv - 50) / 49) for vv in v], edgecolor='none', zorder=1); axz.add_collection(pc)
    iy, ix = np.nonzero(a >= 100); lx, ly, lid = cells(g)
    sq = squares(ix, iy)
    axz.add_collection(PatchCollection([Polygon(q) for q, l in zip(sq, lid) if l], facecolor='#2b3a67', edgecolor='white', lw=0.3, zorder=2))
    axz.add_collection(PatchCollection([Polygon(q) for q, l in zip(sq, lid) if not l], facecolor='#e8730c', edgecolor='white', lw=0.3, zorder=2))
    axz.add_patch(plt.Rectangle((0, 0), 0, 0, fc='#2b3a67', label='치명 · 라이다')); axz.add_patch(plt.Rectangle((0, 0), 0, 0, fc='#e8730c', label='치명 · 카메라만'))
    axz.add_patch(plt.Rectangle((0, 0), 0, 0, fc=plt.get_cmap('Greys')(0.4), label='팽창(비용 50 이상)'))
    tr = min(trajs, key=lambda q: abs(q[0] - T)); Mt = tr[3]
    if len(tr[1]): cx, cy = to_map(Mt, tr[1][:, 0], tr[1][:, 1]); axz.scatter(cx, cy, s=9, c='#374151', zorder=3, label='MPPI 후보 궤적 점(10 개 × 8)')
    if len(tr[2]): ox2, oy2 = to_map(Mt, tr[2][:, 0], tr[2][:, 1]); axz.plot(ox2, oy2, '-o', ms=2.5, color='#c62828', lw=1.6, zorder=4, label='MPPI 최적 궤적(3.2 s)')
    tp = min(tplans, key=lambda q: abs(q[0] - T))
    if len(tp[1]): px, py = to_map(tp[2], tp[1][:, 0], tp[1][:, 1]); axz.plot(px, py, color='#2e7d32', lw=1.6, ls='--', zorder=3, label='따라가는 경로')
    axz.add_patch(Polygon(foot(P), closed=True, fill=False, ec='#111827', lw=2.0, zorder=5))
    axz.annotate('', (P[0] + 0.3 * math.cos(P[2]), P[1] + 0.3 * math.sin(P[2])), (P[0], P[1]), arrowprops=dict(arrowstyle='->', color='#111827', lw=1.5), zorder=6)
    cl = [q for q in CLR if abs(q[0] - ts) < 0.01]
    axz.set_xlim(P[0] - 0.75, P[0] + 0.75); axz.set_ylim(P[1] - 0.85, P[1] + 0.65); axz.set_aspect('equal'); axz.grid(alpha=0.25)
    axz.set_title('%s · %s · 지도 여유 %.1f cm' % (title, time.strftime('%H:%M:%S', time.localtime(ts)), 100 * cl[0][1] if cl else float('nan')), fontsize=10)
    axz.legend(loc='lower left', fontsize=7, framealpha=0.9)


# 지도 여유 시계열(패딩 포함 차체 ↔ 치명 칸 중심)
CLR = []
for g in seg:
    ts, a, (ox_, oy_, r_), M, obp = g; iy, ix = np.nonzero(a >= 100); wx = ox_ + (ix + 0.5) * r_; wy = oy_ + (iy + 0.5) * r_
    c, s = math.cos(obp[2]), math.sin(obp[2]); dx, dy = wx - obp[0], wy - obp[1]; bx = c * dx + s * dy; by = -s * dx + c * dy
    d = np.hypot(np.maximum(np.maximum(PAD[1] - bx, bx - PAD[0]), 0), np.maximum(np.abs(by) - PAD[2], 0)); CLR.append((ts, float(d.min())))
zoom(axA, TA, '(나) A 입구')
zoom(axB, TB, '(다) B 상자 끝')

# (라) 시간축: 여유 · ω · 놓침
CL = np.array(CLR); axC.axhspan(2.7, 4.4, color='#e8730c', alpha=0.15, label='뒤집힘 구간 2.7–4.4 cm'); axC.axhline(6, color='#6b7280', ls=':', lw=1, label='크리틱 띠 6 cm')
axC.plot(CL[:, 0] - T0, 100 * CL[:, 1], '-o', ms=2.5, color='#0f6e8c', lw=1.4, label='지도 여유(차체 ↔ 치명 칸 중심)')
axC.set_ylim(0, 26); axC.set_ylabel('cm'); axC.legend(fontsize=8, loc='lower right', ncol=1, framealpha=0.9); axC.grid(alpha=0.25)
axC.set_title('(라) 시간축 — 위: 지도 여유 · 아래: 회전 명령 ω 와 초당 제어 주기 놓침', fontsize=10)
CM = np.array(cmds); axW.plot(CM[:, 0] - T0, CM[:, 2], color='#6d28d9', lw=1.0, label='명령 ω (rad/s, + = 왼쪽 = 상자 쪽)')
axW.axhline(0, color='#9ca3af', lw=0.8)
miss = {}
for l in open(missf, encoding='utf-8'):
    mm = re.match(r'놓침 (\d\d:\d\d:\d\d) (\d+)', l)
    if mm: miss[tsec(day, mm.group(1))] = int(mm.group(2))
ms_t = np.array(sorted(miss)); ms_n = np.array([miss[k] for k in ms_t]); kk = (ms_t >= T0 - 1) & (ms_t <= T1)
axW.bar(ms_t[kk] - T0 + 0.5, ms_n[kk] / 10 * 0.4, width=0.8, bottom=-0.45, color='#b3261e', alpha=0.35, label='초당 놓침(막대 높이 0.4 = 10 회 = 전부)')
axW.set_ylim(-0.46, 0.42); axW.set_ylabel('ω (rad/s)'); axW.set_xlabel('시간 (s, %s 부터)' % T0s); axW.legend(fontsize=8, loc='upper right'); axW.grid(alpha=0.25)
for axx in (axC, axW):
    for lab, T in (('A', TA), ('B', TB), ('정지', TS)): axx.axvline(T - T0, color='#c62828', lw=0.9, ls='--'); axx.text(T - T0 + 0.2, axx.get_ylim()[1] * 0.85, lab, color='#c62828', fontsize=9)
axC.set_xlim(0, T1 - T0)
fig.suptitle('f2w2 (no5 · ClearanceBandCritic 켬 · 2026-10-15 17:3x) 서쪽 통로 남행 — 움직임과 장애물', fontsize=13, y=0.995)
fig.savefig(out, dpi=115, bbox_inches='tight'); print('그림', out, '· 코스트맵 프레임', len(seg), '· 칸', len(acc))
