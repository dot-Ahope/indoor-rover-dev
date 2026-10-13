#!/usr/bin/env python3
"""fig_box_approach_video — 로버가 장애물(상자)에 다가가 멈추기까지를 지도 좌표 영상으로 만든다. (2026-10-13)
  왜: f2o1 목표 3 정지. 상자 칸이 언제 코스트맵에 있었는지, 전역 경로가 어디로 그려졌는지, 로버가 어떻게 다가갔는지를 한 화면에서 본다.
  화면: 바탕 = 전역 코스트맵(계획기가 보는 지도, 빨강 = 치명·주황 = 내접·회색 = 감쇠), 빨간 테두리 네모 = 로컬 코스트맵의 치명 칸(MPPI 가 보는 것),
        파란 점 = 라이다, 초록 = 차체와 지나온 길, 보라 선 = 전역 경로(/plan), 노란 부채꼴 = 카메라 시야(좌우 ±43°, 1.4 m = nvblox 통합 거리),
        검은 십자 = 정지 때의 상자 칸(anal_box_history 와 같은 정의). 아래 글 = 그 순간의 수치.
  사용: fig_box_approach_video.py bag 출력.mp4 시작HH:MM:SS 정지HH:MM:SS [배속=2.5]"""
import sys, time, math
from pathlib import Path
import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.animation import FFMpegWriter
from matplotlib.colors import ListedColormap
from scipy import ndimage
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
plt.rcParams['font.family'] = 'Malgun Gothic'; plt.rcParams['axes.unicode_minus'] = False; plt.rcParams['animation.ffmpeg_path'] = 'C:/ffmpeg/bin/ffmpeg.exe'
bag, out, h0, h1 = sys.argv[1:5]; SPEED = float(sys.argv[5]) if len(sys.argv) > 5 else 2.5; FPS = 10; DT = SPEED / FPS
FP = np.array([[0.262, 0.165], [0.262, -0.165], [-0.248, -0.165], [-0.248, 0.165]]); HFOV = math.radians(43); CAMR = 1.4


def T3(tr):
    q = tr.rotation; x, y, z, w = q.x, q.y, q.z, q.w; M = np.eye(4)
    M[:3, :3] = [[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)], [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)], [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]]
    M[:3, 3] = [tr.translation.x, tr.translation.y, tr.translation.z]; return M


static = {}; ob = []; mo = []; loc = []; glo = []; plans = []; scans = []
with AnyReader([Path(bag)], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
    t0 = None
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/tf', '/tf_static', '/local_costmap/costmap', '/global_costmap/costmap', '/plan', '/scan')]):
        ts = t / 1e9
        if t0 is None:
            t0 = ts; day = time.strftime('%Y-%m-%d ', time.localtime(t0)); ep = lambda s: time.mktime(time.strptime(day + s, '%Y-%m-%d %H:%M:%S')); tA, tB = ep(h0), ep(h1)
        if c.topic == '/tf_static':
            for tr in rd.deserialize(raw, c.msgtype).transforms: static[tr.child_frame_id] = (tr.header.frame_id, T3(tr.transform))
        elif c.topic == '/tf':
            if ts < tA - 2 or ts > tB + 6: continue
            for tr in rd.deserialize(raw, c.msgtype).transforms:
                if tr.child_frame_id == 'base_link' and tr.header.frame_id == 'odom': ob.append((ts, T3(tr.transform)))
                elif tr.child_frame_id == 'odom' and tr.header.frame_id == 'map': mo.append((ts, T3(tr.transform)))
        elif c.topic == '/global_costmap/costmap' or c.topic == '/plan':
            if ts > tB + 6: continue
            m = rd.deserialize(raw, c.msgtype)
            if c.topic == '/plan': plans.append((ts, np.array([[q.pose.position.x, q.pose.position.y] for q in m.poses])))
            else: glo.append((ts, m.info.origin.position.x, m.info.origin.position.y, m.info.resolution, np.array(m.data, dtype=np.int16).reshape(m.info.height, m.info.width)))
        elif ts < tA - 2 or ts > tB + 6: continue
        elif c.topic == '/local_costmap/costmap':
            m = rd.deserialize(raw, c.msgtype); loc.append((ts, m.info.origin.position.x, m.info.origin.position.y, m.info.resolution, np.array(m.data, dtype=np.int16).reshape(m.info.height, m.info.width)))
        else:
            m = rd.deserialize(raw, c.msgtype); r = np.array(m.ranges); a = m.angle_min + np.arange(len(r)) * m.angle_increment; ok = np.isfinite(r) & (r > m.range_min) & (r < 5)
            scans.append((ts, m.header.frame_id, np.c_[r[ok] * np.cos(a[ok]), r[ok] * np.sin(a[ok]), np.zeros(ok.sum()), np.ones(ok.sum())]))


def chain(frame):
    M = np.eye(4)
    while frame != 'base_link': par, m = static[frame]; M = m @ M; frame = par
    return M
def last(L, ts):
    k = np.searchsorted([x[0] for x in L], ts, side='right') - 1; return L[max(k, 0)]
def w2(M, P): return (M @ np.c_[P[:, 0], P[:, 1], np.zeros(len(P)), np.ones(len(P))].T).T[:, :2]
def leth_cells(g, thr=100):
    _, ox, oy, res, G = g; L = np.argwhere(G >= thr); return np.c_[ox + (L[:, 1] + 0.5) * res, oy + (L[:, 0] + 0.5) * res]
def clear(M_mb, P):   # 지도 좌표 점들까지 차체 여유
    pb = w2(np.linalg.inv(M_mb), P); dx = np.maximum.reduce([FP[:, 0].min() - pb[:, 0], np.zeros(len(pb)), pb[:, 0] - FP[:, 0].max()]); dy = np.maximum.reduce([FP[:, 1].min() - pb[:, 1], np.zeros(len(pb)), pb[:, 1] - FP[:, 1].max()])
    return np.hypot(dx, dy).min()


# 상자 = 정지 때 로컬 코스트맵에서 차체에 가장 가까운 치명 칸이 속한 덩어리(anal_box_history 와 같은 정의), 지도 좌표
g = last(loc, tB); Mmb = last(mo, tB)[1] @ last(ob, tB)[1]; _, ox, oy, res, G = g; L = np.argwhere(G >= 100); Lo = np.c_[ox + (L[:, 1] + 0.5) * res, oy + (L[:, 0] + 0.5) * res]
pb = w2(np.linalg.inv(last(ob, tB)[1]), Lo); d = np.hypot(np.maximum.reduce([FP[:, 0].min() - pb[:, 0], np.zeros(len(pb)), pb[:, 0] - FP[:, 0].max()]), np.maximum.reduce([FP[:, 1].min() - pb[:, 1], np.zeros(len(pb)), pb[:, 1] - FP[:, 1].max()]))
lab, _ = ndimage.label(G >= 100, structure=np.ones((3, 3))); sel = lab[L[:, 0], L[:, 1]] == lab[L[int(np.argmin(d)), 0], L[int(np.argmin(d)), 1]]
BOX = w2(last(mo, tB)[1], Lo[sel]); bc = BOX.mean(0)

times = np.arange(tA, tB + 4, DT); trail = np.array([(last(mo, t)[1] @ last(ob, t)[1])[:2, 3] for t in times])
x0, x1 = min(trail[:, 0].min(), bc[0]) - 1.0, max(trail[:, 0].max(), bc[0]) + 1.0; y0, y1 = min(trail[:, 1].min(), bc[1]) - 1.2, max(trail[:, 1].max(), bc[1]) + 1.2
cmap = ListedColormap(['#ffffff'] + ['#%02x%02x%02x' % ((int(235 - 1.1 * i),) * 3) for i in range(1, 99)] + ['#f4a582', '#b2182b'])
fig = plt.figure(figsize=(12.8, 7.2)); ax = fig.add_axes([0.05, 0.2, 0.62, 0.74]); az = fig.add_axes([0.70, 0.2, 0.28, 0.5]); txt = fig.text(0.05, 0.03, '', fontsize=11, va='bottom', linespacing=1.5); head = fig.text(0.70, 0.93, '', fontsize=12, va='top', linespacing=1.6)
wr = FFMpegWriter(fps=FPS, bitrate=2400)
with wr.saving(fig, out, dpi=100):
    for n, t in enumerate(times):
        Mmo = last(mo, t)[1]; Mmb = Mmo @ last(ob, t)[1]; gl = last(glo, t); lc = last(loc, t); sc = last(scans, t); pl = [p for p in plans if p[0] <= t]; pl = pl[-1][1] if pl else np.zeros((0, 2))
        _, gx, gy, gres, GG = gl; LC = w2(Mmo, leth_cells(lc)); SP = (Mmb @ chain(sc[1]) @ sc[2].T).T[:, :2]; body = w2(Mmb, FP); yaw = math.atan2(Mmb[1, 0], Mmb[0, 0]); c = Mmb[:2, 3]
        cam = np.r_[[c], [c + CAMR * np.array([math.cos(yaw + a), math.sin(yaw + a)]) for a in np.linspace(-HFOV, HFOV, 15)]]
        gi = ((BOX[:, 1] - gy) / gres).astype(int); gj = ((BOX[:, 0] - gx) / gres).astype(int); gbox = int((GG[gi, gj] >= 100).sum())
        Pl = w2(np.linalg.inv(Mmo), BOX); _, lx, ly, lres, LG = lc; li = ((Pl[:, 1] - ly) / lres).astype(int); lj = ((Pl[:, 0] - lx) / lres).astype(int); inw = (li >= 0) & (li < LG.shape[0]) & (lj >= 0) & (lj < LG.shape[1])
        lbox = '%d / %d' % ((LG[li[inw], lj[inw]] >= 100).sum(), len(BOX)) if inw.all() else '창 밖'
        pd = np.hypot(pl[:, None, 0] - BOX[None, :, 0], pl[:, None, 1] - BOX[None, :, 1]).min() if len(pl) else float('nan'); bb = w2(np.linalg.inv(Mmb), BOX).mean(0); brg = math.degrees(math.atan2(bb[1], bb[0])); dist = np.hypot(*bb)
        for a_, (vx0, vx1, vy0, vy1) in ((ax, (x0, x1, y0, y1)), (az, (bc[0] - 0.75, bc[0] + 0.75, bc[1] - 0.75, bc[1] + 0.75))):
            a_.clear(); a_.imshow(np.clip(GG, 0, 100), origin='lower', extent=(gx, gx + GG.shape[1] * gres, gy, gy + GG.shape[0] * gres), cmap=cmap, vmin=0, vmax=100, interpolation='nearest', zorder=0)
            big = a_ is az
            a_.fill(cam[:, 0], cam[:, 1], color='#ffd92f', alpha=0.28, lw=0, zorder=1)
            a_.scatter(LC[:, 0], LC[:, 1], s=60 if big else 9, marker='s', facecolors='none', edgecolors='#d6002a', linewidths=1.1 if big else 0.6, zorder=3)
            a_.scatter(SP[:, 0], SP[:, 1], s=7 if big else 2, color='#2166ac', zorder=4)
            if len(pl): a_.plot(pl[:, 0], pl[:, 1], color='#7b3294', lw=2.0, zorder=5)
            a_.plot(trail[:n + 1, 0], trail[:n + 1, 1], color='#1b7837', lw=1.2, alpha=0.7, zorder=5); a_.plot(*np.r_[body, body[:1]].T, color='#1b7837', lw=2.2, zorder=6)
            a_.annotate('', xy=w2(Mmb, np.array([[0.262, 0]]))[0], xytext=c, arrowprops=dict(arrowstyle='->', color='#1b7837', lw=1.6), zorder=7)
            a_.scatter(BOX[:, 0], BOX[:, 1], s=90 if big else 22, marker='+', color='black', linewidths=1.6 if big else 0.9, zorder=8)
            a_.set_xlim(vx0, vx1); a_.set_ylim(vy0, vy1); a_.set_aspect('equal'); a_.tick_params(labelsize=8)
        ax.set_xlabel('map x (m)'); ax.set_ylabel('map y (m)'); ax.set_title('전역 코스트맵(바탕) 위의 로버·경로 — 보라 = 전역 경로, 빨간 네모 = 로컬 치명 칸, 노랑 = 카메라 시야, + = 상자 칸(정지 때 기준)', fontsize=10, loc='left')
        az.set_title('상자 주변 1.5 m 확대', fontsize=10, loc='left')
        head.set_text('%s  (%.1f배속)\n목표 3 출발 뒤 %.0f s' % (time.strftime('%H:%M:%S', time.localtime(t)), SPEED, t - tA))
        txt.set_text('상자까지 %.2f m · 방위 %+.0f°(%s)   |   차체 여유 %.1f cm   |   전역 경로가 상자 칸에 가장 가까운 거리 %.2f m\n상자 자리의 치명 칸 수 — 전역 코스트맵(계획기) %d / %d   ·   로컬 코스트맵(MPPI) %s' % (
            dist, brg, '카메라 시야 안' if abs(brg) <= 43 and dist <= CAMR else ('시야각 안 · 1.4 m 밖' if abs(brg) <= 43 else '시야 밖'), clear(Mmb, BOX) * 100, pd, gbox, len(BOX), lbox))
        wr.grab_frame()
print('저장', out, '프레임', len(times), '상자 칸', len(BOX), '중심 (%.2f, %.2f)' % tuple(bc))
