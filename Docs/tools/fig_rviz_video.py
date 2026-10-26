#!/usr/bin/env python3
"""fig_rviz_video — 주행 구간을 RViz 스타일(어두운 바탕 · 1 m 격자 · costmap 색표 · 초록 경로 · 빨간 라이다 · 차체 외곽 · 좌표축)로 정사각 영상 (2026-10-26 §17).
  왜: 사용자 — "실촬영 영상과 시각화 데이터 합쳐달라. 시각화 영상은 rviz 스타일로". 실제 촬영(16:9)과 옆으로 붙이기 쉬운 720×720, 로버를 따라가는 창.
  그리는 것(RViz 기본 표시와 같은 뜻):
    · 바탕 = 전역 코스트맵(map), RViz 'costmap' 색표 흉내 — 0 = 비움(바탕 그대로) · 1~98 = 파랑 → 빨강 · 99 내접 = 하늘색 · 100 치명 = 자홍 · −1 미지 = 회청.
    · 로컬 코스트맵 치명 칸(MPPI 가 보는 것) = 노란 테두리 칸, 라이다 /scan = 빨간 점, 전역 경로(BT 경로) = 초록 선, 차체(풋프린트) = 초록 다각형, base_link 축 = 빨강 x · 초록 y.
  BT 경로 고르기 · 데이터 읽기는 fig_drive_video.py 와 같은 규칙(nav_events 의 스무더 사건 + /plan 점 간격 > 0.04 m = Smac).
  사용: fig_rviz_video.py bag 출력.mp4 시작HH:MM:SS 끝HH:MM:SS [배속=1] [nav_events.txt] [제목] [창 m=3.0]"""
import sys, time, math
from pathlib import Path
import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.animation import FFMpegWriter
from matplotlib.colors import ListedColormap
from matplotlib.patches import Polygon
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
plt.rcParams.update({'font.family': 'Malgun Gothic', 'axes.unicode_minus': False, 'animation.ffmpeg_path': 'C:/ffmpeg/bin/ffmpeg.exe'})
bag, out, h0, h1 = sys.argv[1:5]; SPEED = float(sys.argv[5]) if len(sys.argv) > 5 else 1.0; FPS = 10; DT = SPEED / FPS
EVF = sys.argv[6] if len(sys.argv) > 6 and sys.argv[6] != '-' else None; TITLE = sys.argv[7] if len(sys.argv) > 7 else Path(bag).name.replace('bag_', '')
VW = float(sys.argv[8]) if len(sys.argv) > 8 else 3.0
FP = np.array([[0.262, 0.165], [0.262, -0.165], [-0.248, -0.165], [-0.248, 0.165]])
BG = '#303030'; GRIDC = '#a0a0a4'; GREEN = '#19ff00'; RED = '#ff2a2a'; YEL = '#ffd400'; TXT = '#e8e8e8'


def rviz_costmap_cmap():   # 값 = 코스트맵 값 + 1 (−1 → 0)
    cols = [(0.44, 0.54, 0.53, 0.85), (0, 0, 0, 0)]   # 미지 · 비움(투명)
    for i in range(1, 99):   # 1~98: 파랑 → 빨강
        f = (i - 1) / 97.0; cols.append((f, 0.0, 1.0 - f, 0.18 + 0.27 * f))   # RViz 처럼 파랑→빨강, 낮은 비용은 더 투명(경로 · 차체가 묻히지 않게)
    cols += [(0.0, 1.0, 1.0, 0.45), (1.0, 0.0, 1.0, 0.85)]   # 99 내접 하늘색 · 100 치명 자홍
    return ListedColormap(cols)


def T3(tr):
    q = tr.rotation; x, y, z, w = q.x, q.y, q.z, q.w; M = np.eye(4)
    M[:3, :3] = [[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)], [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)], [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]]
    M[:3, 3] = [tr.translation.x, tr.translation.y, tr.translation.z]; return M


static = {}; ob = []; mo = []; loc = []; glo = []; plans = []; raws = []; scans = []; cmds = []
with AnyReader([Path(bag)], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
    t0 = None
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/tf', '/tf_static', '/local_costmap/costmap', '/global_costmap/costmap', '/plan', '/plan_smoothed', '/scan', '/cmd_vel')]):
        ts = t / 1e9
        if t0 is None:
            t0 = ts; day = time.strftime('%Y-%m-%d ', time.localtime(t0)); ep = lambda s: time.mktime(time.strptime(day + s, '%Y-%m-%d %H:%M:%S')); tA, tB = ep(h0), ep(h1)
        if c.topic == '/tf_static':
            for tr in rd.deserialize(raw, c.msgtype).transforms: static[tr.child_frame_id] = (tr.header.frame_id, T3(tr.transform))
            continue
        if ts > tB + 2 or (ts < tA - 3 and c.topic not in ('/global_costmap/costmap', '/plan', '/plan_smoothed', '/tf')): continue
        m = rd.deserialize(raw, c.msgtype)
        if c.topic == '/tf':
            for tr in m.transforms:
                if tr.child_frame_id == 'base_link' and tr.header.frame_id == 'odom': ob.append((ts, T3(tr.transform)))
                elif tr.child_frame_id == 'odom' and tr.header.frame_id == 'map': mo.append((ts, T3(tr.transform)))
        elif c.topic in ('/plan', '/plan_smoothed'):
            if len(m.poses) > 1: (plans if c.topic == '/plan_smoothed' else raws).append((ts, np.array([[p.pose.position.x, p.pose.position.y] for p in m.poses])))
        elif c.topic == '/cmd_vel': cmds.append((ts, m.linear.x, m.angular.z))
        elif c.topic == '/scan':
            r = np.array(m.ranges); a = m.angle_min + np.arange(len(r)) * m.angle_increment; ok = np.isfinite(r) & (r > m.range_min) & (r < 6)
            scans.append((ts, m.header.frame_id, np.c_[r[ok] * np.cos(a[ok]), r[ok] * np.sin(a[ok]), np.zeros(ok.sum()), np.ones(ok.sum())]))
        else:
            g = (ts, m.info.origin.position.x, m.info.origin.position.y, m.info.resolution, np.array(m.data, dtype=np.int16).reshape(m.info.height, m.info.width)); (glo if c.topic.startswith('/global') else loc).append(g)
for L in (ob, mo, plans, raws, cmds, scans, loc, glo): L.sort(key=lambda q: q[0])
NEV = []
if EVF:   # BT 경로(스무더 사건) · 사건 줄
    bt = []
    for line in open(EVF, encoding='utf-8', errors='replace'):
        te = time.mktime(time.strptime(day + line[:8], '%Y-%m-%d %H:%M:%S')) + float(line[8:11])
        if 'Received a path to smooth' in line: bt.append([te, True])
        elif 'Smoothed path leads to a collision' in line and bt: bt[-1][1] = False
        lab = ('막힘 감지' if '2.0 s 지속되면' in line else '막힘 → 주행 중단' if '주행 중단' in line else '복구 ' + line.split('Running ')[-1].strip() if 'Running' in line else
               '최적화 실패' if 'Optimizer fail' in line else 'Smac 실패 → NavFn' if 'SmacHybrid failed' in line else 'TF 외삽 → 중단' if 'extrapolation into the future' in line else '목표 도착' if 'Goal succeeded' in line else None)
        if lab and tA - 1 <= te <= tB + 1: NEV.append((te, lab))
    sel = []
    for te, ok_ in bt:
        cand = [q for q in plans if 0 <= q[0] - te + 0.05 < 1.5] if ok_ else []
        if cand: sel.append(cand[0]); continue
        cand = [q for q in raws if 0 <= te + 0.05 - q[0] < 1.5]
        if cand: sel.append((te, cand[-1][1]))
    plans = sel
plans += [q for q in raws if len(q[1]) > 3 and np.median(np.hypot(*np.diff(q[1], axis=0).T)) > 0.04]   # Smac 경로
plans.sort(key=lambda q: q[0])


def chain(frame):
    M = np.eye(4)
    while frame != 'base_link': par, mm = static[frame]; M = mm @ M; frame = par
    return M
def last(L, t): return L[max(np.searchsorted([x[0] for x in L], t, side='right') - 1, 0)]
def w2(M, P): return (M @ np.c_[P[:, 0], P[:, 1], np.zeros(len(P)), np.ones(len(P))].T).T[:, :2]
times = np.arange(tA, tB, DT); CM = rviz_costmap_cmap()
fig = plt.figure(figsize=(7.2, 7.2), dpi=100, facecolor=BG); ax = fig.add_axes([0, 0, 1, 1]); ax.set_facecolor(BG); ax.set_axis_off()
gext = lambda g: (g[1], g[1] + g[4].shape[1] * g[3], g[2], g[2] + g[4].shape[0] * g[3])
g0 = glo[0]; im = ax.imshow(np.clip(g0[4], -1, 100) + 1, origin='lower', extent=gext(g0), cmap=CM, vmin=0, vmax=101, interpolation='nearest', zorder=1)
gl_lines = []
loc_s = ax.scatter([], [], marker='s', facecolors='none', edgecolors=YEL, linewidths=0.9, zorder=3)
scan_s = ax.scatter([], [], s=4, color=RED, zorder=4, lw=0)
path_l, = ax.plot([], [], color=GREEN, lw=2.6, zorder=5)
trail_l, = ax.plot([], [], color='#ffffff', lw=1.0, alpha=0.5, zorder=5)
body = Polygon(FP, closed=True, fill=False, ec=GREEN, lw=2.0, zorder=6); ax.add_patch(body)
axx, = ax.plot([], [], color='#ff0000', lw=2.5, zorder=7); axy, = ax.plot([], [], color='#00ff00', lw=2.5, zorder=7)
tx = fig.text(0.02, 0.98, '', color=TXT, fontsize=11, va='top', bbox=dict(fc='#000000', alpha=0.55, ec='none'))
ev = fig.text(0.02, 0.03, '', color=YEL, fontsize=12, va='bottom', fontweight='bold', bbox=dict(fc='#000000', alpha=0.55, ec='none'))
fig.text(0.98, 0.98, TITLE, color=TXT, fontsize=10, va='top', ha='right', bbox=dict(fc='#000000', alpha=0.55, ec='none'))
fig.text(0.98, 0.03, '전역 costmap: 파랑→빨강 비용 · 하늘색 내접 · 자홍 치명 | 노랑 □ 로컬 치명 | 빨강 라이다 | 초록 경로 · 차체', color=TXT, fontsize=7.5, va='bottom', ha='right')
px_per_m = 720 / VW; loc_s.set_sizes([(0.05 * px_per_m * 0.72 * 0.85) ** 2])
trail = np.array([(last(mo, t)[1] @ last(ob, t)[1])[:2, 3] for t in times])
gid = None; wr = FFMpegWriter(fps=FPS, bitrate=4000)
with wr.saving(fig, out, dpi=100):
    for n, t in enumerate(times):
        Mmo = last(mo, t)[1]; Mmb = Mmo @ last(ob, t)[1]; c = Mmb[:2, 3]; yaw = math.atan2(Mmb[1, 0], Mmb[0, 0])
        gl = last(glo, t)
        if id(gl) != gid: gid = id(gl); im.set_data(np.clip(gl[4], -1, 100) + 1); im.set_extent(gext(gl))
        ax.set_xlim(c[0] - VW / 2, c[0] + VW / 2); ax.set_ylim(c[1] - VW / 2, c[1] + VW / 2)
        for l_ in gl_lines: l_.remove()
        gl_lines = [ax.axvline(x, color=GRIDC, lw=0.6, alpha=0.45, zorder=2) for x in np.arange(math.floor(c[0] - VW), c[0] + VW, 1.0)] + \
                   [ax.axhline(y, color=GRIDC, lw=0.6, alpha=0.45, zorder=2) for y in np.arange(math.floor(c[1] - VW), c[1] + VW, 1.0)]
        _, lx, ly, lr, LG = last(loc, t); L = np.argwhere(LG >= 100)
        loc_s.set_offsets(w2(Mmo, np.c_[lx + (L[:, 1] + 0.5) * lr, ly + (L[:, 0] + 0.5) * lr]) if len(L) else np.zeros((0, 2)))
        sc = last(scans, t); scan_s.set_offsets((Mmb @ chain(sc[1]) @ sc[2].T).T[:, :2])
        p = [q for q in plans if q[0] <= t]; pl = p[-1][1] if p else np.zeros((0, 2)); path_l.set_data(pl[:, 0], pl[:, 1])
        trail_l.set_data(trail[:n + 1, 0], trail[:n + 1, 1]); body.set_xy(w2(Mmb, FP))
        o = c; xa = w2(Mmb, np.array([[0.3, 0.0]]))[0]; ya = w2(Mmb, np.array([[0.0, 0.3]]))[0]
        axx.set_data([o[0], xa[0]], [o[1], xa[1]]); axy.set_data([o[0], ya[0]], [o[1], ya[1]])
        cm = last(cmds, t) if cmds else (0, 0, 0)
        tx.set_text('%s  ×%g\ncmd v %+.3f m/s  ω %+.2f rad/s\n로버 (%.2f, %.2f) %+.0f°' % (time.strftime('%H:%M:%S', time.localtime(t)) + '.%d' % int(t % 1 * 10), SPEED, cm[1], cm[2], c[0], c[1], math.degrees(yaw)))
        rec = [lab for te, lab in NEV if t - 2.5 <= te <= t]; ev.set_text('● ' + rec[-1] if rec else '')
        wr.grab_frame()
print('저장', out, '프레임', len(times), '· 경로', len(plans))
