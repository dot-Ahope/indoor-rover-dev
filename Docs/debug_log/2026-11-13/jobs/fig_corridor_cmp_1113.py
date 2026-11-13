#!/usr/bin/env python3
# fig_corridor_cmp_1113 — 11-13 §3: 서쪽 통로(목표 3~6)를 f2rr1(11-11, 문제 없음)과 f2rd1(11-13, 막힘 · 후진 많음)으로 나란히.
#   전역 코스트맵(f2rr1 = PC bag 을 rosbags 로, f2rd1 = Jetson 에서 잘라 온 npz) 위에 러너 csv 궤적 · 막힘 지점.
#   PC, 로버 안 움직임. 인자: f2rr1 bag 폴더 · f2rd1 crop 출력(txt, 'NPZ ' 줄) · f2rr1 csv · f2rd1 csv · 출력 png
#   막힘 지점은 outputs/nav_events_f2rd1_live.txt 의 PathBlockedAhead '지속 →' 줄(손으로 옮김 — 아래 BLK).
import sys, io, base64, csv, datetime, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from pathlib import Path
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
bag1, crop2, csv1, csv2, outp = sys.argv[1:6]
KST = datetime.timezone(datetime.timedelta(hours=9))
X0, X1, Y0, Y1 = -2.8, -0.8, -6.0, -1.6
def crop_from_bag(bag, hms, day):
    t = datetime.datetime.fromisoformat(f'{day}T{hms}').replace(tzinfo=KST).timestamp() * 1e9
    ts = get_typestore(Stores.ROS2_HUMBLE); best = None
    with AnyReader([Path(bag)], default_typestore=ts) as r:
        con = [c for c in r.connections if c.topic == '/global_costmap/costmap']
        for c, stamp, raw in r.messages(connections=con):
            if best is None or abs(stamp - t) < abs(best[0] - t): best = (stamp, raw, c)
            if stamp > t + 5e9: break
        m = r.deserialize(best[1], best[2].msgtype)
    i = m.info; g = np.array(m.data, dtype=np.int16).reshape(i.height, i.width)
    c0 = int((X0 - i.origin.position.x) / i.resolution); r0 = int((Y0 - i.origin.position.y) / i.resolution)
    c1 = int((X1 - i.origin.position.x) / i.resolution); r1 = int((Y1 - i.origin.position.y) / i.resolution)
    return g[r0:r1, c0:c1], (i.origin.position.x + c0 * i.resolution, i.origin.position.y + r0 * i.resolution, i.resolution)
def crop_from_npz(txt, key):
    z = np.load(io.BytesIO(base64.b64decode([l for l in open(txt, encoding='utf-8', errors='replace') if l.startswith('NPZ ')][0][4:])))
    m = z['meta' + key]; return z['g' + key], (m[2], m[3], m[1])
def traj(f):
    return [(int(r['goal']), float(r['map_x']), float(r['map_y']), float(r['v'])) for r in csv.DictReader(open(f))]
BLK = [(-1.82, -2.87), (-1.97, -2.97), (-1.58, -4.53), (-2.01, -3.09), (-1.87, -3.10)]   # f2rd1 막힘 정지 지점(nav_events_f2rd1_live.txt)
panels = [('f2rr1 (11-11) — 문제 없음', crop_from_bag(bag1, '14:55:44', '2026-11-11'), traj(csv1), []),
          ('f2rd1 (11-13) — 15:48:03 첫 막힘', crop_from_npz(crop2, '154803'), traj(csv2), BLK),
          ('f2rd1 (11-13) — 15:49:06', crop_from_npz(crop2, '154906'), traj(csv2), BLK)]
plt.rcParams['font.family'] = ['Malgun Gothic', 'DejaVu Sans']
fig, ax = plt.subplots(1, 3, figsize=(15, 9))
col = {3: '#1f77b4', 4: '#2ca02c', 5: '#d62728', 6: '#9467bd'}
for a, (title, (g, (ox, oy, res)), tr, blk) in zip(ax, panels):
    ext = [ox, ox + g.shape[1] * res, oy, oy + g.shape[0] * res]
    show = np.where(g < 0, 50, g).astype(float)
    a.imshow(show, origin='lower', extent=ext, cmap='Greys', vmin=0, vmax=100)
    a.contour(np.where(g >= 99, 1, 0), levels=[0.5], origin='lower', extent=ext, colors='orange', linewidths=0.8)
    for gl in (3, 4, 5, 6):
        p = [(x, y) for G, x, y, v in tr if G == gl]
        if p: a.plot(*zip(*p), '-', color=col[gl], lw=1.4, label=f'목표 {gl}')
        q = [(x, y) for G, x, y, v in tr if G == gl and v < -0.005]
        if q: a.plot(*zip(*q), '.', color='k', ms=3)
    for x, y in blk: a.plot(x, y, 'x', color='red', ms=10, mew=2)
    a.set_title(title, fontsize=11); a.set_xlim(X0, X1); a.set_ylim(Y0, Y1); a.set_aspect('equal'); a.grid(alpha=0.3)
ax[0].legend(loc='lower right', fontsize=9)
fig.suptitle('서쪽 통로 전역 코스트맵(주황 = 비용 ≥ 99 경계) · 궤적(검은 점 = 후진) · 빨간 X = f2rd1 막힘 정지', fontsize=12)
fig.tight_layout(); fig.savefig(outp, dpi=110); print('saved', outp)
