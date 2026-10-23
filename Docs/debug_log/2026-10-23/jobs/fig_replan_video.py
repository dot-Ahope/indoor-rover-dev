#!/usr/bin/env python3
"""fig_replan_video — Docs/tools/fig_run_video.py 사본 + 경로 위 막힘 표시 · nav2 사건 줄 (2026-10-23 §19).
  왜: 사용자 — "전역 경로 위에 장애물이 나올 경우 어떻게 경로를 수정하는지 설명 + 영상". 추가: ① 확대 판에 PathBlockedAhead 가 보는 구간(로버 앞 경로 0.30~1.5 m)과
     그 구간의 전역 비용 ≥ 99 점(빨간 ×) ② 아래 글에 최근 3 s 안 nav2 사건. 사용: fig_replan_video.py bag 출력.mp4 시작 끝 배속 nav_events.txt
  (아래는 원판 설명)
  fig_run_video — 주행 한 구간을 지도 좌표 영상으로 만든다(특정 장애물 없이 주행 전체를 보는 일반판). (2026-10-14)
  왜: f2r2 에서 로버 앞으로 사람이 지나갔을 때 경로를 고쳤다가 사람이 사라지자 다시 고친 것으로 보였다(사용자 관찰) — 전역 경로가 언제 어떻게 바뀌었는지 눈으로 확인.
  화면: 왼쪽 = 주행 구역 전체, 오른쪽 = 로버 주변 3 × 3 m 확대(로버 따라감).
        바탕 = 전역 코스트맵(계획기가 보는 지도: 빨강 치명 · 주황 내접 · 회색 감쇠), 보라 선 = 지금 전역 경로, 옅은 보라 = 직전 경로(바뀐 뒤 3 s 동안),
        빨간 네모 = 로컬 코스트맵 치명 칸(MPPI 가 보는 것), 파란 점 = 라이다, 초록 = 차체와 지나온 길, 노란 부채꼴 = 카메라 시야(±43°, 1.4 m).
        아래 글 = 속도, 경로 길이, 앞쪽 가장 가까운 라이다 점, 경로가 바뀐 횟수.
  끝에 경로 길이가 0.3 m 넘게 달라진 시각을 표로 낸다(사람이 지나간 순간 찾기용).
  [10-14 추가] 오른쪽 확대 판에 목표 방향 두 개를 화살표로: 보라 = 계획기 경로(/plan) 끝 방향(원래 목표), 주황 = 컨트롤러가 받은 경로(/transformed_global_plan) 끝 방향.
        둘이 다르면 컨트롤러는 주황 쪽으로 돌려고 한다(§13.1 BT TruncatePath 결함 확인용). 아래 글에 두 방향과 로버 방향을 숫자로.
  사용: fig_run_video.py bag 출력.mp4 시작HH:MM:SS 끝HH:MM:SS [배속=3]"""
import sys, time, math
from pathlib import Path
import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.animation import FFMpegWriter
from matplotlib.colors import ListedColormap
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
plt.rcParams['font.family'] = 'Malgun Gothic'; plt.rcParams['axes.unicode_minus'] = False; plt.rcParams['animation.ffmpeg_path'] = 'C:/ffmpeg/bin/ffmpeg.exe'
bag, out, h0, h1 = sys.argv[1:5]; SPEED = float(sys.argv[5]) if len(sys.argv) > 5 else 3.0; FPS = 10; DT = SPEED / FPS
EVF = sys.argv[6] if len(sys.argv) > 6 else None
FP = np.array([[0.262, 0.165], [0.262, -0.165], [-0.248, -0.165], [-0.248, 0.165]]); HFOV = math.radians(43); CAMR = 1.4


def T3(tr):
    q = tr.rotation; x, y, z, w = q.x, q.y, q.z, q.w; M = np.eye(4)
    M[:3, :3] = [[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)], [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)], [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]]
    M[:3, 3] = [tr.translation.x, tr.translation.y, tr.translation.z]; return M


static = {}; ob = []; mo = []; loc = []; glo = []; plans = []; scans = []; cmds = []; tplans = []
with AnyReader([Path(bag)], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
    t0 = None
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/tf', '/tf_static', '/local_costmap/costmap', '/global_costmap/costmap', '/plan', '/scan', '/cmd_vel', '/transformed_global_plan')]):
        ts = t / 1e9
        if t0 is None:
            t0 = ts; day = time.strftime('%Y-%m-%d ', time.localtime(t0)); ep = lambda s: time.mktime(time.strptime(day + s, '%Y-%m-%d %H:%M:%S')); tA, tB = ep(h0), ep(h1)
        if c.topic == '/tf_static':
            for tr in rd.deserialize(raw, c.msgtype).transforms: static[tr.child_frame_id] = (tr.header.frame_id, T3(tr.transform))
            continue
        if ts > tB + 2 or (ts < tA - 3 and c.topic not in ('/global_costmap/costmap', '/plan')): continue
        m = rd.deserialize(raw, c.msgtype)
        if c.topic == '/tf':
            for tr in m.transforms:
                if tr.child_frame_id == 'base_link' and tr.header.frame_id == 'odom': ob.append((ts, T3(tr.transform)))
                elif tr.child_frame_id == 'odom' and tr.header.frame_id == 'map': mo.append((ts, T3(tr.transform)))
        elif c.topic == '/plan':
            if len(m.poses) > 1: plans.append((ts, np.array([[q.pose.position.x, q.pose.position.y] for q in m.poses]), math.atan2(2 * (m.poses[-1].pose.orientation.w * m.poses[-1].pose.orientation.z), 1 - 2 * m.poses[-1].pose.orientation.z ** 2)))
        elif c.topic == '/cmd_vel': cmds.append((ts, m.linear.x, m.angular.z))
        elif c.topic == '/transformed_global_plan':
            if len(m.poses): q = m.poses[-1].pose; tplans.append((ts, q.position.x, q.position.y, math.atan2(2 * (q.orientation.w * q.orientation.z), 1 - 2 * q.orientation.z ** 2)))
        elif c.topic == '/scan':
            r = np.array(m.ranges); a = m.angle_min + np.arange(len(r)) * m.angle_increment; ok = np.isfinite(r) & (r > m.range_min) & (r < 6); scans.append((ts, m.header.frame_id, np.c_[r[ok] * np.cos(a[ok]), r[ok] * np.sin(a[ok]), np.zeros(ok.sum()), np.ones(ok.sum())]))
        else:
            g = (ts, m.info.origin.position.x, m.info.origin.position.y, m.info.resolution, np.array(m.data, dtype=np.int16).reshape(m.info.height, m.info.width)); (glo if c.topic.startswith('/global') else loc).append(g)


def chain(frame):
    M = np.eye(4)
    while frame != 'base_link': par, mm = static[frame]; M = mm @ M; frame = par
    return M
def last(L, t): return L[max(np.searchsorted([x[0] for x in L], t, side='right') - 1, 0)]
def w2(M, P): return (M @ np.c_[P[:, 0], P[:, 1], np.zeros(len(P)), np.ones(len(P))].T).T[:, :2]
plen = lambda p: float(np.hypot(*np.diff(p, axis=0).T).sum())
# 경로가 크게 바뀐 시각(같은 목표인데 길이가 0.3 m 넘게 달라짐, 또는 목표가 바뀜)
ev = []
for (ta, pa, *_), (tb, pb, *_) in zip(plans, plans[1:]):
    if tA <= tb <= tB:
        newgoal = np.hypot(*(pa[-1] - pb[-1])) > 0.3; d = plen(pb) - plen(pa)
        if newgoal or abs(d) > 0.3: ev.append((tb, '새 목표' if newgoal else '경로 %+.2f m' % d, plen(pa), plen(pb)))
NEV = []   # (epoch, 이름) — nav2 사건 줄 'HH:MM:SS.cc 노드 메시지'
if EVF:
    for line in open(EVF, encoding='utf-8', errors='replace'):
        lab = ('경로 막힘 감지' if '2.0 s 지속되면' in line else '막힘 2 s 지속 → 주행 중단' if '주행 중단' in line else '새 전역 경로' if 'Received a path to smooth' in line else
               '복구 ' + line.split('Running ')[-1].strip() if 'Running' in line else 'TF 외삽 → 컨트롤러 중단' if 'extrapolation into the future' in line else '목표 도착' if 'Goal succeeded' in line else None)
        if lab: NEV.append((time.mktime(time.strptime(day + line[:8], '%Y-%m-%d %H:%M:%S')) + float(line[8:11]), lab))
times = np.arange(tA, tB, DT); trail = np.array([(last(mo, t)[1] @ last(ob, t)[1])[:2, 3] for t in times])
x0, x1 = trail[:, 0].min() - 1.2, trail[:, 0].max() + 1.2; y0, y1 = trail[:, 1].min() - 1.2, trail[:, 1].max() + 1.2
cmap = ListedColormap(['#ffffff'] + ['#%02x%02x%02x' % ((int(235 - 1.1 * i),) * 3) for i in range(1, 99)] + ['#f4a582', '#b2182b'])
fig = plt.figure(figsize=(12.8, 7.2)); ax = fig.add_axes([0.05, 0.2, 0.60, 0.74]); az = fig.add_axes([0.69, 0.27, 0.29, 0.52]); txt = fig.text(0.05, 0.03, '', fontsize=11, va='bottom', linespacing=1.5); head = fig.text(0.69, 0.93, '', fontsize=12, va='top', linespacing=1.6)
wr = FFMpegWriter(fps=FPS, bitrate=2400); nchg = 0; lastchg = -99.0; prevplan = None; curplan = None
with wr.saving(fig, out, dpi=100):
    for n, t in enumerate(times):
        Mmo = last(mo, t)[1]; Mmb = Mmo @ last(ob, t)[1]; gl = last(glo, t); lc = last(loc, t); sc = last(scans, t); p = [q for q in plans if q[0] <= t]; pl = p[-1][1] if p else np.zeros((0, 2))
        if curplan is None or (len(pl) and (len(pl) != len(curplan) or abs(plen(pl) - plen(curplan)) > 1e-6)):
            if curplan is not None and len(pl) and (abs(plen(pl) - plen(curplan)) > 0.3 or np.hypot(*(pl[-1] - curplan[-1])) > 0.3): nchg += 1; lastchg = t; prevplan = curplan
            curplan = pl
        _, gx, gy, gres, GG = gl; _, lx, ly, lres, LG = lc; L = np.argwhere(LG >= 100); LC = w2(Mmo, np.c_[lx + (L[:, 1] + 0.5) * lres, ly + (L[:, 0] + 0.5) * lres]) if len(L) else np.zeros((0, 2))
        SP = (Mmb @ chain(sc[1]) @ sc[2].T).T[:, :2]; body = w2(Mmb, FP); yaw = math.atan2(Mmb[1, 0], Mmb[0, 0]); c = Mmb[:2, 3]
        cam = np.r_[[c], [c + CAMR * np.array([math.cos(yaw + a), math.sin(yaw + a)]) for a in np.linspace(-HFOV, HFOV, 15)]]
        sb = (np.linalg.inv(Mmb) @ np.c_[SP, np.zeros(len(SP)), np.ones(len(SP))].T).T; fr = sb[(sb[:, 0] > 0.262) & (np.abs(sb[:, 1]) < 0.30)]; ahead = fr[:, 0].min() - 0.262 if len(fr) else float('nan')
        cm = last(cmds, t) if cmds else (0, 0, 0)
        gyaw = p[-1][2] if p else None; gend = pl[-1] if len(pl) else None; cyaw = None; cend = None
        if tplans:
            tp = last(tplans, t)
            if t - tp[0] < 5: cend = w2(Mmo, np.array([[tp[1], tp[2]]]))[0]; cyaw = tp[3] + math.atan2(Mmo[1, 0], Mmo[0, 0])   # odom → map
        for a_, (vx0, vx1, vy0, vy1) in ((ax, (x0, x1, y0, y1)), (az, (c[0] - 1.5, c[0] + 1.5, c[1] - 1.5, c[1] + 1.5))):
            a_.clear(); a_.imshow(np.clip(GG, 0, 100), origin='lower', extent=(gx, gx + GG.shape[1] * gres, gy, gy + GG.shape[0] * gres), cmap=cmap, vmin=0, vmax=100, interpolation='nearest', zorder=0)
            big = a_ is az
            a_.fill(cam[:, 0], cam[:, 1], color='#ffd92f', alpha=0.28, lw=0, zorder=1)
            if len(LC): a_.scatter(LC[:, 0], LC[:, 1], s=34 if big else 8, marker='s', facecolors='none', edgecolors='#d6002a', linewidths=0.9 if big else 0.5, zorder=3)
            a_.scatter(SP[:, 0], SP[:, 1], s=6 if big else 2, color='#2166ac', zorder=4)
            if prevplan is not None and t - lastchg < 3.0 * SPEED / 3 + 3.0 and len(prevplan): a_.plot(prevplan[:, 0], prevplan[:, 1], color='#c2a5cf', lw=1.6, ls='--', zorder=5)
            if len(pl): a_.plot(pl[:, 0], pl[:, 1], color='#7b3294', lw=2.0, zorder=6)
            a_.plot(trail[:n + 1, 0], trail[:n + 1, 1], color='#1b7837', lw=1.2, alpha=0.7, zorder=6); a_.plot(*np.r_[body, body[:1]].T, color='#1b7837', lw=2.2, zorder=7)
            a_.annotate('', xy=w2(Mmb, np.array([[0.262, 0]]))[0], xytext=c, arrowprops=dict(arrowstyle='->', color='#1b7837', lw=1.6), zorder=8)
            if big and len(pl) > 2:   # PathBlockedAhead 검사 구간(로버에서 가장 가까운 경로점부터 0.30~1.5 m)과 그 구간의 비용 ≥ 99 점
                i0 = int(np.argmin(np.linalg.norm(pl - c, axis=1))); sacc = np.r_[0, np.cumsum(np.linalg.norm(np.diff(pl[i0:], axis=0), axis=1))]
                seg = pl[i0:][(sacc >= 0.30) & (sacc <= 1.5)]
                if len(seg):
                    ij = (((seg[:, 1] - gy) / gres).astype(int), ((seg[:, 0] - gx) / gres).astype(int)); okk = (ij[0] >= 0) & (ij[0] < GG.shape[0]) & (ij[1] >= 0) & (ij[1] < GG.shape[1])
                    vv = np.zeros(len(seg)); vv[okk] = GG[ij[0][okk], ij[1][okk]]; bad = seg[vv >= 99]
                    a_.plot(seg[:, 0], seg[:, 1], color='#ff7f00', lw=3.5, alpha=0.35, zorder=5)
                    if len(bad): a_.scatter(bad[:, 0], bad[:, 1], s=60, marker='x', color='#e31a1c', linewidths=2.2, zorder=11)
            if big and gend is not None and gyaw is not None: a_.annotate('', xy=(gend[0] + 0.45 * math.cos(gyaw), gend[1] + 0.45 * math.sin(gyaw)), xytext=gend, arrowprops=dict(arrowstyle='-|>', color='#7b3294', lw=2.6), zorder=9)
            if big and cend is not None: a_.annotate('', xy=(cend[0] + 0.45 * math.cos(cyaw), cend[1] + 0.45 * math.sin(cyaw)), xytext=cend, arrowprops=dict(arrowstyle='-|>', color='#dd6b20', lw=2.6), zorder=10)
            a_.set_xlim(vx0, vx1); a_.set_ylim(vy0, vy1); a_.set_aspect('equal'); a_.tick_params(labelsize=8)
        ax.set_xlabel('map x (m)'); ax.set_ylabel('map y (m)'); ax.set_title('보라 = 전역 경로(점선 = 직전) · 빨간 네모 = 로컬 치명 칸 · 파랑 = 라이다 · 노랑 = 카메라 시야', fontsize=9.5, loc='left')
        az.set_title('로버 주변 3 × 3 m · 주황 띠 = 막힘 검사 구간(앞 0.3~1.5 m) · 빨간 × = 그 구간 비용 ≥ 99', fontsize=8.5, loc='left')
        head.set_text('%s  (%.1f배속)\n구간 시작 뒤 %.0f s' % (time.strftime('%H:%M:%S', time.localtime(t)), SPEED, t - tA))
        dirs = '목표 방향(보라) %s · 컨트롤러가 받은 끝 방향(주황) %s · 로버 %+.0f°' % ('%+.0f°' % math.degrees(gyaw) if gyaw is not None else '-', '%+.0f°' % math.degrees(cyaw) if cyaw is not None else '-', math.degrees(yaw))
        txt.set_text('명령 속도 %.3f m/s · %+.2f rad/s   |   전역 경로 길이 %.2f m   |   경로 급변 %d 회%s\n%s' % (
            cm[1], cm[2], plen(pl) if len(pl) > 1 else 0.0, nchg, (' ← 방금(점선 = 직전 경로)' if t - lastchg < 4.0 else ''), dirs)
            + '\n사건(최근 3 s): ' + (' → '.join(dict.fromkeys(lab for te, lab in NEV if t - 3.0 <= te <= t)) or '—'))
        wr.grab_frame()
print('저장', out, '프레임', len(times))
print('경로가 크게 바뀐 시각(같은 목표에서 길이 0.3 m 넘게 변화 또는 새 목표):')
for tb, why, la, lb in ev: print('  %s  %s  (%.2f → %.2f m)' % (time.strftime('%H:%M:%S', time.localtime(tb)), why, la, lb))
