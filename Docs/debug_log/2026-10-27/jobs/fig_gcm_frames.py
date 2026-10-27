#!/usr/bin/env python3
"""fig_gcm_frames — §15 전역 코스트맵 메시지 연속 몇 장을 같은 창으로 나란히(밝은 색표 = fig_rviz_video light) + 같은 시각 로컬 코스트맵 (2026-10-27, PC).
  인자: bag폴더 출력.png 창(x0,x1,y0,y1) 시각1 시각2 …(HH:MM:SS.ff — 그 시각 직후 첫 메시지)"""
import sys, time, math
import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from pathlib import Path
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
plt.rcParams.update({'font.family': 'Malgun Gothic', 'axes.unicode_minus': False})
bag = Path(sys.argv[1]); out = sys.argv[2]; X0, X1, Y0, Y1 = map(float, sys.argv[3].split(','))
def ts_of(s):
    h, m, r = s.split(':'); return time.mktime(time.strptime('2026-10-27 %s:%s:00' % (h, m), '%Y-%m-%d %H:%M:%S')) + float(r)
WANT = [ts_of(s) for s in sys.argv[4:]]
cmap = ListedColormap(np.r_[[[0.98, 0.95, 0.80]], np.linspace([1, 1, 1], [0.78, 0.80, 0.84], 99), [[0.45, 0.47, 0.52]], [[0.08, 0.09, 0.11]]])
hs = lambda t: time.strftime('%H:%M:%S', time.localtime(t)) + '.%02d' % int((t % 1) * 100)
def yaw(q): return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
GM, LM, mo = [], [], []
with AnyReader([bag], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/global_costmap/costmap', '/local_costmap/costmap', '/tf')]):
        ts = t * 1e-9
        if ts < min(WANT) - 5 or ts > max(WANT) + 5: continue
        m = rd.deserialize(raw, c.msgtype)
        if c.topic == '/tf':
            for tr in m.transforms:
                if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom': mo.append((ts, tr.transform.translation.x, tr.transform.translation.y, yaw(tr.transform.rotation)))
            continue
        i = m.info; (GM if c.topic[1] == 'g' else LM).append((ts, np.array(m.data, np.int16).reshape(i.height, i.width), i.origin.position.x, i.origin.position.y, i.resolution))
fig, axs = plt.subplots(2, len(WANT), figsize=(3.6 * len(WANT), 7.4))
for k, w in enumerate(WANT):
    g = next(x for x in GM if x[0] >= w); ts, G, ox, oy, r = g
    a = axs[0, k]; a.imshow(G + 1, origin='lower', extent=(ox, ox + G.shape[1] * r, oy, oy + G.shape[0] * r), cmap=cmap, vmin=0, vmax=101, interpolation='nearest')
    a.set_xlim(X0, X1); a.set_ylim(Y0, Y1); a.set_aspect('equal'); a.set_title('전역 %s' % hs(ts), fontsize=10); a.tick_params(labelsize=7)
    l = min(LM, key=lambda x: abs(x[0] - ts)); lt, L, lox, loy, lr = l
    T = min(mo, key=lambda x: abs(x[0] - lt)); c_, s_ = math.cos(T[3]), math.sin(T[3])
    J, I = np.nonzero(L == 100); xo, yo = lox + (I + .5) * lr, loy + (J + .5) * lr
    b = axs[1, k]; b.imshow(G + 1, origin='lower', extent=(ox, ox + G.shape[1] * r, oy, oy + G.shape[0] * r), cmap=cmap, vmin=0, vmax=101, interpolation='nearest', alpha=0.35)
    b.scatter(T[1] + c_ * xo - s_ * yo, T[2] + s_ * xo + c_ * yo, s=9, marker='s', color='#e8590c')
    b.set_xlim(X0, X1); b.set_ylim(Y0, Y1); b.set_aspect('equal'); b.set_title('로컬 치명(주황) %s' % hs(lt), fontsize=10); b.tick_params(labelsize=7)
fig.suptitle('f2st1 전역 코스트맵 연속 메시지(위) · 같은 시각 로컬 치명 칸(아래, 바탕 = 전역 옅게) — map 좌표', x=0.01, ha='left', fontsize=12)
fig.tight_layout(); fig.savefig(out, dpi=100); print('저장', out)
