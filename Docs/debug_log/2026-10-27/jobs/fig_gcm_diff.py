#!/usr/bin/env python3
"""fig_gcm_diff — §15 틀어진 전역 프레임에서 새로 생긴 · 사라진 치명 칸과, 그 사이 라이다 스캔(map 으로 옮김)을 겹쳐 그림 (2026-10-27, PC).
  인자: bag폴더 출력.png 창(x0,x1,y0,y1) 틀어진프레임시각1 [시각2 …](HH:MM:SS.ff 직후 첫 전역 메시지)"""
import sys, time, math
import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from pathlib import Path
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
plt.rcParams.update({'font.family': 'Malgun Gothic', 'axes.unicode_minus': False})
bag = Path(sys.argv[1]); out = sys.argv[2]; X0, X1, Y0, Y1 = map(float, sys.argv[3].split(','))
def ts_of(s):
    h, m, r = s.split(':'); return time.mktime(time.strptime('2026-10-27 %s:%s:00' % (h, m), '%Y-%m-%d %H:%M:%S')) + float(r)
WANT = [ts_of(s) for s in sys.argv[4:]]
hs = lambda t: time.strftime('%H:%M:%S', time.localtime(t)) + '.%02d' % int((t % 1) * 100)
def yaw(q): return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
def T3(tr):
    a = yaw(tr.rotation); c, s = math.cos(a), math.sin(a); return np.array([[c, -s, tr.translation.x], [s, c, tr.translation.y], [0, 0, 1]])
GM, SC, mo, ob, static = [], [], [], [], {}
with AnyReader([bag], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/global_costmap/costmap', '/scan', '/tf', '/tf_static')]):
        ts = t * 1e-9; m = None
        if c.topic == '/tf_static':
            for tr in rd.deserialize(raw, c.msgtype).transforms: static[tr.child_frame_id] = (tr.header.frame_id, T3(tr.transform))
            continue
        if ts < min(WANT) - 6 or ts > max(WANT) + 4: continue
        m = rd.deserialize(raw, c.msgtype)
        if c.topic == '/tf':
            for tr in m.transforms:
                if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom': mo.append((ts, T3(tr.transform)))
                elif tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link': ob.append((ts, T3(tr.transform)))
        elif c.topic == '/scan':
            a = m.angle_min + m.angle_increment * np.arange(len(m.ranges)); r = np.array(m.ranges, np.float32); ok = np.isfinite(r) & (r > m.range_min) & (r < m.range_max)
            SC.append((ts, m.header.stamp.sec + m.header.stamp.nanosec * 1e-9, m.header.frame_id, np.c_[r[ok] * np.cos(a[ok]), r[ok] * np.sin(a[ok]), np.ones(ok.sum())]))
        else:
            i = m.info; GM.append((ts, np.array(m.data, np.int16).reshape(i.height, i.width), i.origin.position.x, i.origin.position.y, i.resolution))
near = lambda L, t: min(L, key=lambda x: abs(x[0] - t))[1]
def chain(f):
    M = np.eye(3)
    while f != 'base_link': p, mm = static[f]; M = mm @ M; f = p
    return M
fig, axs = plt.subplots(1, len(WANT), figsize=(6.4 * len(WANT), 6.4)); axs = np.atleast_1d(axs)
for a, w in zip(axs, WANT):
    k = next(j for j, x in enumerate(GM) if x[0] >= w); ts, G, ox, oy, r = GM[k]; Pv, Nx = GM[k - 1][1], GM[k + 1][1]
    cell = lambda msk: (ox + (np.nonzero(msk)[1] + .5) * r, oy + (np.nonzero(msk)[0] + .5) * r)
    keep = (G == 100) & (Pv == 100); add = (G == 100) & (Pv != 100); rem = (G != 100) & (Pv == 100) & (Nx == 100)
    a.scatter(*cell(keep), s=14, marker='s', color='#c8ccd2', label='직전과 같은 치명')
    a.scatter(*cell(add), s=14, marker='s', color='#d6336c', label='새로 생긴 치명 %d' % add.sum())
    a.scatter(*cell(rem), s=14, marker='s', facecolor='none', edgecolor='#1c7ed6', label='잠깐 사라진 치명(다음에 복귀) %d' % rem.sum())
    for s in [x for x in SC if GM[k - 1][0] < x[0] <= ts]:
        Mmb = near(mo, s[0]) @ near(ob, s[0]); W = (Mmb @ chain(s[2]) @ s[3].T).T
        a.plot(W[:, 0], W[:, 1], '.', ms=1.5, color='#0f9d58', alpha=0.5)
    a.plot([], [], '.', color='#0f9d58', label='그 사이 라이다 스캔(현재 TF)')
    Mmb = near(mo, ts) @ near(ob, ts); a.plot(Mmb[0, 2], Mmb[1, 2], 'o', color='#1b1f24', ms=8); a.text(Mmb[0, 2] + 0.05, Mmb[1, 2] + 0.05, '로버', fontsize=9)
    a.set_xlim(X0, X1); a.set_ylim(Y0, Y1); a.set_aspect('equal'); a.grid(color='#eceef1')
    a.set_title('전역 %s vs 직전 %s' % (hs(ts), hs(GM[k - 1][0])), loc='left', fontsize=11); a.legend(fontsize=8.5, loc='lower left')
fig.tight_layout(); fig.savefig(out, dpi=100); print('저장', out)
