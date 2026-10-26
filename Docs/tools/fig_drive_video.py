#!/usr/bin/env python3
"""fig_drive_video — 주행 한 구간을 영상으로(1920 × 1080). fig_run_video · 10-23 fig_replan_video 의 화면 재설계판 (2026-10-23 §20.5).
  왜: 사용자 — "동영상 시각화에 사용한 파이썬 코드의 디자인이 별로". 데이터 처리는 같고 화면만 바꿈:
    · 큰 판 = 로버를 따라가는 확대 지도(주인공), 오른쪽 위 = 구간 전체 미니맵(지나온 길 · 지금 보는 창), 오른쪽 = 시각 · 상태 · 범례, 아래 = 사건 시간줄(재생 위치 표시).
    · 코스트맵은 차분한 색(빈 칸 흰색 · 감쇠 옅은 회색 · 내접 연한 살구 · 치명 짙은 회청)으로 깔고, 빨강 · 주황은 경고(막힘 검사 구간 · 막힌 점)에만 씀.
  그리는 것: 전역 코스트맵(계획기가 보는 지도), 전역 경로(보라, 바뀐 직후 3 s 는 직전 경로 회색 점선), 로컬 치명 칸(MPPI 가 보는 것, 자홍 테두리 칸),
    라이다 점, 카메라 시야, 차체 · 지나온 길, PathBlockedAhead 검사 구간(로버 앞 경로 0.30~1.5 m)과 그 안 비용 ≥ 99 점, 경로 끝 목표 방향.
  사용: fig_drive_video.py bag 출력.mp4 시작HH:MM:SS 끝HH:MM:SS [배속=2] [nav_events.txt] [제목]
    nav_events.txt = 'HH:MM:SS.cc 노드 메시지' 줄(예: Docs/debug_log/2026-10-23/outputs/nav_events_ms_f2rp3.txt)"""
import sys, time, math
from pathlib import Path
import numpy as np, matplotlib
import matplotlib.markers
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.animation import FFMpegWriter
from matplotlib.colors import ListedColormap
from matplotlib.patches import Rectangle, Polygon, Patch
from matplotlib.lines import Line2D
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
plt.rcParams.update({'font.family': 'Malgun Gothic', 'axes.unicode_minus': False, 'animation.ffmpeg_path': 'C:/ffmpeg/bin/ffmpeg.exe'})
bag, out, h0, h1 = sys.argv[1:5]; SPEED = float(sys.argv[5]) if len(sys.argv) > 5 else 2.0; FPS = 10; DT = SPEED / FPS
EVF = sys.argv[6] if len(sys.argv) > 6 and sys.argv[6] != '-' else None; TITLE = sys.argv[7] if len(sys.argv) > 7 else Path(bag).name.replace('bag_', '')
FP = np.array([[0.262, 0.165], [0.262, -0.165], [-0.248, -0.165], [-0.248, 0.165]]); HFOV = math.radians(43); CAMR = 1.4
VIEW_W = 3.6   # 확대 판 가로(m)

# ── 색(역할별 하나씩) ──
INK, INK2, MUTED, GRID = '#1f2328', '#57606a', '#8c959f', '#d0d7de'
BG, PANEL = '#ffffff', '#f6f8fa'
C_PATH, C_PREV, C_ROVER, C_TRAIL = '#5b3cc4', '#8c959f', '#0f766e', '#14b8a6'
C_LOCAL, C_SCAN, C_CAM = '#c2255c', '#1c4e80', '#f2c94c'
C_CHECK, C_BLOCK = '#f08c00', '#e03131'
C_INSCR, C_LETHAL = '#fbe3cc', '#3b4252'
# 코스트맵: −1 미지 · 0 빈 칸 · 1~98 감쇠(옅은 회색 단계) · 99 내접 · 100 치명
CM = ListedColormap(['#eceff1', '#ffffff'] + ['#%02x%02x%02x' % tuple(int(a + (b - a) * i / 97) for a, b in zip((246, 246, 244), (196, 199, 204))) for i in range(98)] + [C_INSCR, C_LETHAL])
EVSTYLE = {'새 전역 경로': C_PATH, '경로 막힘 감지': C_CHECK, '막힘 2 s → 주행 중단': C_BLOCK, '복구': INK, 'TF 외삽 → 중단': MUTED, '목표 도착': C_ROVER, '최적화 실패': '#9c36b5'}


def T3(tr):
    q = tr.rotation; x, y, z, w = q.x, q.y, q.z, q.w; M = np.eye(4)
    M[:3, :3] = [[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)], [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)], [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]]
    M[:3, 3] = [tr.translation.x, tr.translation.y, tr.translation.z]; return M


raws = []; static = {}; ob = []; mo = []; loc = []; glo = []; plans = []; scans = []; cmds = []
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
        elif c.topic in ('/plan', '/plan_smoothed'):   # 어느 것이 BT 경로였는지는 아래에서 nav2 사건으로 가림
            if len(m.poses) > 1:
                q = m.poses[-1].pose.orientation; (plans if c.topic == '/plan_smoothed' else raws).append((ts, np.array([[p.pose.position.x, p.pose.position.y] for p in m.poses]), math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))))
        elif c.topic == '/cmd_vel': cmds.append((ts, m.linear.x, m.angular.z))
        elif c.topic == '/scan':
            r = np.array(m.ranges); a = m.angle_min + np.arange(len(r)) * m.angle_increment; ok = np.isfinite(r) & (r > m.range_min) & (r < 6); scans.append((ts, m.header.frame_id, np.c_[r[ok] * np.cos(a[ok]), r[ok] * np.sin(a[ok]), np.zeros(ok.sum()), np.ones(ok.sum())]))
        else:
            g = (ts, m.info.origin.position.x, m.info.origin.position.y, m.info.resolution, np.array(m.data, dtype=np.int16).reshape(m.info.height, m.info.width)); (glo if c.topic.startswith('/global') else loc).append(g)
for L in (ob, mo, plans, cmds, scans, loc, glo): L.sort(key=lambda q: q[0])


def chain(frame):
    M = np.eye(4)
    while frame != 'base_link': par, mm = static[frame]; M = mm @ M; frame = par
    return M
def last(L, t): return L[max(np.searchsorted([x[0] for x in L], t, side='right') - 1, 0)]
def w2(M, P): return (M @ np.c_[P[:, 0], P[:, 1], np.zeros(len(P)), np.ones(len(P))].T).T[:, :2]
plen = lambda p: float(np.hypot(*np.diff(p, axis=0).T).sum())
NEV = []
if EVF:
    for line in open(EVF, encoding='utf-8', errors='replace'):
        lab = ('경로 막힘 감지' if '2.0 s 지속되면' in line else '막힘 2 s → 주행 중단' if '주행 중단' in line else '새 전역 경로' if 'Received a path to smooth' in line else
               '복구' if 'Running' in line else 'TF 외삽 → 중단' if 'extrapolation into the future' in line else '목표 도착' if 'Goal succeeded' in line else
               '최적화 실패' if 'Optimizer fail' in line else None)
        if lab:
            te = time.mktime(time.strptime(day + line[:8], '%Y-%m-%d %H:%M:%S')) + float(line[8:11])
            det = line.split('Running ')[-1].strip() if lab == '복구' else ''
            if tA - 1 <= te <= tB + 1 and not (NEV and NEV[-1][1] == lab and te - NEV[-1][0] < 0.3): NEV.append((te, lab, det))
# ★ 10-23 §20.7 정정: BT 가 컨트롤러에 준 경로 = 스무딩 성공이면 /plan_smoothed, 실패('Smoothed path leads to a collision')면 원경로 /plan(CopyPath).
#   첫 판은 /plan_smoothed 만 그려, 스무딩이 실패한 동안(f2rp4 서쪽 통로 경로 4 개) 화면 경로가 묵은 것이었다. nav_events 가 있으면 BT 계획마다 골라 씀.
#   /plan 에는 러너 조회기 경로도 섞이므로 BT 계획 시각('Received a path to smooth')에 가장 가까운 것만.
if EVF:
    bt = []
    for line in open(EVF, encoding='utf-8', errors='replace'):
        if 'Received a path to smooth' in line or 'Smoothed path leads to a collision' in line:
            te = time.mktime(time.strptime(day + line[:8], '%Y-%m-%d %H:%M:%S')) + float(line[8:11])
            if 'Received' in line: bt.append([te, True])
            elif bt: bt[-1][1] = False
    sel = []
    for te, ok in bt:
        cand = [q for q in plans if 0 <= q[0] - te + 0.05 < 1.5] if ok else []
        if cand: sel.append(cand[0]); continue
        cand = [q for q in raws if 0 <= te + 0.05 - q[0] < 1.5]
        if cand: sel.append((te,) + tuple(cand[-1][1:]))
    if sel: plans = sorted(sel, key=lambda q: q[0]); print("BT 경로 %d 개(원경로 %d)" % (len(sel), sum(1 for te, ok in bt if not ok)))
# 2026-10-26 §8: planner:=smac 주행은 BT 경로가 Smac(→ CopyPath) 이라 스무더 사건이 없음 → /plan 중 점 간격 중앙 > 0.04 m(Smac ≈ 0.07, 러너 조회 NavFn 0.025)를 BT 경로로
if not any('Received a path to smooth' in l for l in (open(EVF, encoding='utf-8', errors='replace') if EVF else [])):
    sm = [q for q in raws if len(q[1]) > 3 and np.median(np.hypot(*np.diff(q[1], axis=0).T)) > 0.04]
    if sm: plans = sorted(sm + plans, key=lambda q: q[0]); print('Smac 경로 %d 개(점 간격 > 0.04 m)' % len(sm))
times = np.arange(tA, tB, DT); trail = np.array([(last(mo, t)[1] @ last(ob, t)[1])[:2, 3] for t in times])
x0, x1 = trail[:, 0].min() - 1.0, trail[:, 0].max() + 1.0; y0, y1 = trail[:, 1].min() - 1.0, trail[:, 1].max() + 1.0

# ── 화면 틀(한 번만 만들고 매 장 값만 바꿈) ──
fig = plt.figure(figsize=(19.2, 10.8), dpi=100, facecolor=BG)
AX_MAIN = [0.03, 0.18, 0.58, 0.755]; az = fig.add_axes(AX_MAIN)
VIEW_H = VIEW_W * (AX_MAIN[3] * 10.8) / (AX_MAIN[2] * 19.2)
mm_h = 0.30; mm_w = mm_h * 10.8 / 19.2 * (x1 - x0) / (y1 - y0)
if mm_w > 0.33: mm_w = 0.33; mm_h = mm_w * 19.2 / 10.8 * (y1 - y0) / (x1 - x0)
am = fig.add_axes([0.64, 0.935 - mm_h, mm_w, mm_h]); at = fig.add_axes([0.045, 0.035, 0.93, 0.075])
fig.text(0.025, 0.965, TITLE, fontsize=20, fontweight='bold', color=INK, va='center')
fig.text(0.61, 0.965, '로버를 따라가는 %.1f × %.1f m 창 · 바탕 = 전역 코스트맵(계획기가 보는 지도)' % (VIEW_W, VIEW_H), fontsize=12, color=INK2, va='center', ha='right')
fig.text(0.64, 0.955, '구간 전체', fontsize=11, color=INK2, va='bottom')
clock = fig.text(0.64, 0.935 - 0.30 - 0.03, '', fontsize=30, color=INK, va='top', fontweight='bold', family='Consolas')
sub = fig.text(0.64, 0.935 - 0.30 - 0.088, '', fontsize=12, color=INK2, va='top')
stat_y = 0.935 - 0.30 - 0.128
stat_lab = ['명령 속도', '회전 지령', '전역 경로 길이', '로버 방향', '경로 끝 목표 방향']
stats = []
for i, s in enumerate(stat_lab):
    fig.text(0.64, stat_y - i * 0.029, s, fontsize=12, color=INK2, va='top')
    stats.append(fig.text(0.76, stat_y - i * 0.029, '', fontsize=13, color=INK, va='top', family='Consolas'))
evbox = fig.text(0.64, stat_y - 5 * 0.029 - 0.008, '', fontsize=13, va='top', color=C_BLOCK, fontweight='bold')
leg = [Patch(facecolor=C_LETHAL, label='치명 칸(전역)'), Patch(facecolor=C_INSCR, label='내접 칸 = 99 (빠듯)'), Patch(facecolor='#d5d8dc', label='감쇠(멀수록 옅음)'),
       Line2D([], [], color=C_PATH, lw=3, label='전역 경로'), Line2D([], [], color=C_PREV, lw=2, ls='--', label='직전 경로(바뀐 뒤 3 s)'),
       Line2D([], [], color=C_CHECK, lw=7, alpha=0.5, label='막힘 검사 구간 0.3~1.5 m'), Line2D([], [], marker='o', ls='', mfc=C_BLOCK, mec='white', ms=11, label='검사 구간의 비용 ≥ 99 점'),
       Line2D([], [], marker='s', ls='', mfc='none', mec=C_LOCAL, ms=9, label='로컬 치명 칸(MPPI)'), Line2D([], [], marker='o', ls='', color=C_SCAN, ms=4, label='라이다'),
       Patch(facecolor=C_ROVER, alpha=0.35, edgecolor=C_ROVER, label='차체 · 지나온 길'), Patch(facecolor=C_CAM, alpha=0.3, label='카메라 시야')]
fig.legend(handles=leg, loc='lower left', bbox_to_anchor=(0.635, 0.112), ncol=2, frameon=False, fontsize=11, handlelength=2.2, columnspacing=1.5, labelcolor=INK2)

for a_ in (az, am):
    for s in a_.spines.values(): s.set_color(GRID)
    a_.tick_params(labelsize=10, colors=MUTED, length=0)
az.set_xlabel('map x (m)', color=MUTED, fontsize=10); az.set_ylabel('map y (m)', color=MUTED, fontsize=10)
am.set_xticks([]); am.set_yticks([])
gl0 = glo[0]
def gext(g): return (g[1], g[1] + g[4].shape[1] * g[3], g[2], g[2] + g[4].shape[0] * g[3])
cmg = lambda G: np.clip(G, -1, 100) + 1
im_main = az.imshow(cmg(gl0[4]), origin='lower', extent=gext(gl0), cmap=CM, vmin=0, vmax=101, interpolation='nearest', zorder=0)
im_mini = am.imshow(cmg(gl0[4]), origin='lower', extent=gext(gl0), cmap=CM, vmin=0, vmax=101, interpolation='nearest', zorder=0)
am.set_xlim(x0, x1); am.set_ylim(y0, y1); am.set_aspect('equal')
am.plot(trail[:, 0], trail[:, 1], color=GRID, lw=1.5, zorder=1)
mm_tr, = am.plot([], [], color=C_TRAIL, lw=2.2, zorder=2); mm_dot, = am.plot([], [], 'o', color=C_ROVER, ms=7, zorder=4)
mm_box = Rectangle((0, 0), VIEW_W, VIEW_H, fill=False, ec=INK, lw=1.2, zorder=3); am.add_patch(mm_box)
mm_path, = am.plot([], [], color=C_PATH, lw=1.4, zorder=2)
# 확대 판 요소
cam_p = Polygon(np.zeros((3, 2)), closed=True, fc=C_CAM, alpha=0.22, ec=C_CAM, lw=0.8, zorder=1); az.add_patch(cam_p)
prev_l, = az.plot([], [], color=C_PREV, lw=2.0, ls=(0, (5, 4)), zorder=5)
chk_l, = az.plot([], [], color=C_CHECK, lw=11, alpha=0.40, solid_capstyle='round', zorder=5)
path_l, = az.plot([], [], color=C_PATH, lw=3.0, zorder=6, solid_capstyle='round')
local_s = az.scatter([], [], marker='s', facecolors='none', edgecolors=C_LOCAL, linewidths=0.9, alpha=0.85, zorder=3)
scan_s = az.scatter([], [], s=7, color=C_SCAN, zorder=4, lw=0)
trail_l, = az.plot([], [], color=C_TRAIL, lw=2.0, alpha=0.8, zorder=6)
body_p = Polygon(FP, closed=True, fc=C_ROVER, alpha=0.30, ec=C_ROVER, lw=2.4, zorder=7); az.add_patch(body_p)
head_l, = az.plot([], [], color=C_ROVER, lw=2.4, zorder=8)
block_s = az.scatter([], [], s=150, color=C_BLOCK, edgecolors='white', linewidths=2.0, zorder=11)
goal_l, = az.plot([], [], color=C_PATH, lw=3.0, zorder=9); goal_h = az.scatter([], [], s=90, color=C_PATH, zorder=9)
# 로컬 칸 크기(점²): 칸 0.05 m 를 화면 점으로
px_per_m = AX_MAIN[2] * 19.2 * 72 / VIEW_W
local_s.set_sizes([(0.05 * px_per_m * 0.82) ** 2])
# 사건 시간줄
at.set_xlim(tA, tB); at.set_ylim(0, 1); at.set_yticks([]); [s.set_visible(False) for k, s in at.spines.items() if k != 'bottom']; at.spines['bottom'].set_color(GRID)
tk = np.arange(math.ceil(tA / 10) * 10, tB, 10); at.set_xticks(tk); at.set_xticklabels([time.strftime('%H:%M:%S', time.localtime(v)) for v in tk], fontsize=10, color=MUTED); at.tick_params(length=3, colors=MUTED)
rows = {'새 전역 경로': 0.82, '경로 막힘 감지': 0.62, '막힘 2 s → 주행 중단': 0.62, '복구': 0.40, '최적화 실패': 0.40, 'TF 외삽 → 중단': 0.40, '목표 도착': 0.18}
for te, lab, det in NEV: at.plot([te], [rows[lab]], marker='|' if lab == '새 전역 경로' else 'o', ms=14 if lab == '새 전역 경로' else 7, mew=2.2, color=EVSTYLE[lab], ls='')
fig.text(0.025, 0.118, '사건  │ 세로 막대 = 새 전역 경로 · 주황 = 막힘 감지 · 빨강 = 주행 중단 · 검정 = 복구(탈출 · 대기) · 초록 = 목표 도착', fontsize=10.5, color=INK2)
for lab_, y_ in (('경로', 0.82), ('막힘', 0.62), ('복구', 0.40), ('도착', 0.18)): at.text(tA - (tB - tA) * 0.004, y_, lab_, ha='right', va='center', fontsize=9.5, color=MUTED)
play = at.axvline(tA, color=INK, lw=1.6)

wr = FFMpegWriter(fps=FPS, bitrate=6000); prevplan = None; curplan = None; lastchg = -99.0; gid = None
with wr.saving(fig, out, dpi=100):
    for n, t in enumerate(times):
        Mmo = last(mo, t)[1]; Mmb = Mmo @ last(ob, t)[1]; gl = last(glo, t); lc = last(loc, t); sc = last(scans, t); p = [q for q in plans if q[0] <= t]
        pl = p[-1][1] if p else np.zeros((0, 2))
        if p and (curplan is None or p[-1][0] != curplan[0]):
            if curplan is not None: prevplan = curplan[1]; lastchg = t
            curplan = p[-1]
        if id(gl) != gid: gid = id(gl); im_main.set_data(cmg(gl[4])); im_main.set_extent(gext(gl)); im_mini.set_data(cmg(gl[4])); im_mini.set_extent(gext(gl))
        c = Mmb[:2, 3]; yaw = math.atan2(Mmb[1, 0], Mmb[0, 0])
        az.set_xlim(c[0] - VIEW_W / 2, c[0] + VIEW_W / 2); az.set_ylim(c[1] - VIEW_H / 2, c[1] + VIEW_H / 2); az.set_aspect('equal')
        _, lx, ly, lres, LG = lc; L = np.argwhere(LG >= 100)
        local_s.set_offsets(w2(Mmo, np.c_[lx + (L[:, 1] + 0.5) * lres, ly + (L[:, 0] + 0.5) * lres]) if len(L) else np.zeros((0, 2)))
        scan_s.set_offsets((Mmb @ chain(sc[1]) @ sc[2].T).T[:, :2])
        cam_p.set_xy(np.r_[[c], [c + CAMR * np.array([math.cos(yaw + a), math.sin(yaw + a)]) for a in np.linspace(-HFOV, HFOV, 21)]])
        body_p.set_xy(w2(Mmb, FP)); hd = w2(Mmb, np.array([[0.0, 0.0], [0.36, 0.0]])); head_l.set_data(hd[:, 0], hd[:, 1])
        trail_l.set_data(trail[:n + 1, 0], trail[:n + 1, 1]); mm_tr.set_data(trail[:n + 1, 0], trail[:n + 1, 1]); mm_dot.set_data([c[0]], [c[1]])
        mm_box.set_xy((c[0] - VIEW_W / 2, c[1] - VIEW_H / 2))
        path_l.set_data(pl[:, 0], pl[:, 1]); mm_path.set_data(pl[:, 0], pl[:, 1])
        if prevplan is not None and t - lastchg < 3.0: prev_l.set_data(prevplan[:, 0], prevplan[:, 1])
        else: prev_l.set_data([], [])
        bad = np.zeros((0, 2)); chk_l.set_data([], [])
        if len(pl) > 2:   # PathBlockedAhead 검사 구간과 그 안의 비용 ≥ 99 점
            i0 = int(np.argmin(np.linalg.norm(pl - c, axis=1))); sacc = np.r_[0, np.cumsum(np.linalg.norm(np.diff(pl[i0:], axis=0), axis=1))]
            seg = pl[i0:][(sacc >= 0.30) & (sacc <= 1.5)]
            if len(seg):
                _, gx, gy, gres, GG = gl
                ij = (np.floor((seg[:, 1] - gy) / gres).astype(int), np.floor((seg[:, 0] - gx) / gres).astype(int)); okk = (ij[0] >= 0) & (ij[0] < GG.shape[0]) & (ij[1] >= 0) & (ij[1] < GG.shape[1])
                vv = np.zeros(len(seg)); vv[okk] = GG[ij[0][okk], ij[1][okk]]; bad = seg[vv >= 99]; chk_l.set_data(seg[:, 0], seg[:, 1])
        block_s.set_offsets(bad[:1] if len(bad) else np.zeros((0, 2)))
        if p and len(pl):
            gyaw = p[-1][2]; ge = pl[-1]; tip = ge + 0.35 * np.array([math.cos(gyaw), math.sin(gyaw)])
            goal_l.set_data([ge[0], tip[0]], [ge[1], tip[1]]); goal_h.set_offsets([tip]); goal_h.set_paths([matplotlib.markers.MarkerStyle((3, 0, math.degrees(gyaw) - 90)).get_path().transformed(matplotlib.markers.MarkerStyle((3, 0, math.degrees(gyaw) - 90)).get_transform())])
        cm = last(cmds, t) if cmds else (0, 0, 0)
        clock.set_text(time.strftime('%H:%M:%S', time.localtime(t)) + '.%d' % int((t % 1) * 10))
        sub.set_text('구간 시작 뒤 %5.1f s  ·  %g배속' % (t - tA, SPEED))
        vals = ['%+.3f m/s' % cm[1], '%+.2f rad/s' % cm[2], '%.2f m' % plen(pl) if len(pl) > 1 else '—', '%+.0f°' % math.degrees(yaw), '%+.0f°' % math.degrees(p[-1][2]) if p else '—']
        for s_, v in zip(stats, vals): s_.set_text(v)
        recent = [(te, lab, det) for te, lab, det in NEV if t - 2.5 <= te <= t]
        if recent:
            te, lab, det = recent[-1]; evbox.set_text('● ' + lab + (' (%s)' % det if det else '')); evbox.set_color(EVSTYLE[lab])
        else: evbox.set_text('')
        play.set_xdata([t, t])
        wr.grab_frame()
print('저장', out, '프레임', len(times))
