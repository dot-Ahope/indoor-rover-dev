#!/usr/bin/env python3
"""fig_no5_route — 8 목표 순회 코스(no5)를 저장 지도(office_v3) 위에: 목표 번호 + 실제로 달린 궤적(목표 구간마다 색). (2026-10-14 §27, 오늘만)
  왜: 기준선 코스를 정하기 전에 사용자가 '2 번째 목표(당시 'W3' 로 부른 C)가 낭비 아닌가' 판단하려고 no5 가 실제로 어디로 도는지 보기.
  궤적: bag 의 map→odom ∘ odom→base_link(지도 좌표, 차체 중심). 목표 구간 경계는 러너 csv 의 goal 열이 바뀐 시각(첫 /cmd_vel 기준, ab_windows 와 같은 방법).
  목표 좌표는 PC 러너 run_f2c.sh 의 NO5 문자열과 같다(f = 위치만, p = 방향까지). 이름은 10-01 §8 코스 정의(§27.2 에서 되돌림).
  인자: bag 러너csv 출력.png"""
import sys, time, math, csv
from pathlib import Path
import numpy as np, matplotlib, yaml
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from PIL import Image
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
plt.rcParams['font.family'] = 'Malgun Gothic'; plt.rcParams['axes.unicode_minus'] = False
bag, cs, out = sys.argv[1:4]
G = [(2.25, -1.6, 'p', 'B'), (-1.6, -2.0, 'p', 'C'), (-1.65, -3.7, 'p', '서쪽 통로'), (-1.6, -5.5, 'f', '남서'),
     (-1.65, -3.7, 'p', '서쪽 통로'), (-1.6, -2.1, 'p', '위 복도'), (5.5, -2.2, 'p', 'W3'), (0.0, 0.0, 'p', '출발점')]
yq = lambda q: math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
ob = []; mo = []; T0 = None
with AnyReader([Path(bag)], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/tf', '/cmd_vel')]):
        m = rd.deserialize(raw, c.msgtype)
        if c.topic == '/cmd_vel':
            if T0 is None and (abs(m.linear.x) > 1e-3 or abs(m.angular.z) > 1e-3): T0 = t / 1e9
            continue
        for tr in m.transforms:
            v = (t / 1e9, tr.transform.translation.x, tr.transform.translation.y, yq(tr.transform.rotation))
            if tr.child_frame_id == 'base_link' and tr.header.frame_id == 'odom': ob.append(v)
            elif tr.child_frame_id == 'odom' and tr.header.frame_id == 'map': mo.append(v)
ob = np.array(ob); mo = np.array(mo)
R = list(csv.DictReader(open(cs))); first = {}
for r in R: first.setdefault(int(r['goal']), float(r['t']))
t0c = min(first.values()); bounds = sorted((T0 + v - t0c, k) for k, v in first.items()); tend = T0 + float(R[-1]['t']) - t0c
P = []
for o in ob[::3]:
    if o[0] < T0 - 1 or o[0] > tend + 1: continue
    m = mo[min(np.searchsorted(mo[:, 0], o[0]), len(mo) - 1)]; c, s = math.cos(m[3]), math.sin(m[3])
    g = max([k for tb, k in bounds if tb <= o[0]] or [1])
    P.append((o[0], m[1] + c * o[1] - s * o[2], m[2] + s * o[1] + c * o[2], g))
P = np.array(P)
Y = yaml.safe_load(open('Docs/04_navigation/maps/office_v3.yaml', encoding='utf-8')); img = np.array(Image.open('Docs/04_navigation/maps/office_v3.pgm')); res = Y['resolution']; ox, oy = Y['origin'][:2]
H, W = img.shape; ext = (ox, ox + W * res, oy, oy + H * res)
fig, ax = plt.subplots(figsize=(12, 9.2))
ax.imshow(np.flipud(img), origin='lower', extent=ext, cmap='gray', vmin=0, vmax=255, interpolation='nearest')
cols = plt.get_cmap('tab10').colors
for k in range(1, 9):
    q = P[P[:, 3] == k]
    if len(q): ax.plot(q[:, 1], q[:, 2], color=cols[(k - 1) % 10], lw=2.4, alpha=0.9, label='%d → %s (%.0f s)' % (k, G[k - 1][3], (dict(bounds_rev := {kk: tb for tb, kk in bounds}).get(k + 1, tend) - bounds_rev[k])))
groups = []
for i, (x, y, md, nm) in enumerate(G, 1):
    for gr in groups:
        if math.hypot(gr[0][1] - x, gr[0][2] - y) < 0.15: gr.append((i, x, y, md, nm)); break
    else: groups.append([(i, x, y, md, nm)])
for gr in groups:
    x, y, md = gr[0][1], gr[0][2], gr[0][3]; col = '#c53030' if md == 'f' else '#2b6cb0'
    ax.scatter([x], [y], s=520, color=col, edgecolors='white', linewidths=1.8, zorder=5)
    ax.text(x, y, '·'.join(str(g[0]) for g in gr), color='white', fontsize=10 if len(gr) == 1 else 8.5, fontweight='bold', ha='center', va='center', zorder=6)
    ax.text(x + 0.3, y + 0.28, ' / '.join(sorted({g[4] for g in gr})) + (' · 위치만' if md == 'f' else ''), fontsize=10, zorder=6, bbox=dict(boxstyle='round,pad=0.2', fc='white', ec='none', alpha=0.88))
ax.scatter([-0.35], [0], marker='>', s=200, color='#2f855a', zorder=7)
ax.set_xlim(-3.0, 6.8); ax.set_ylim(-6.6, 1.3); ax.set_aspect('equal'); ax.grid(color='#9aa5ae', lw=0.3, alpha=0.5)
ax.set_xlabel('map x (m)'); ax.set_ylabel('map y (m)')
ax.legend(loc='upper right', fontsize=9, title='구간(색) = 그 목표로 가는 길 · 걸린 시간', title_fontsize=9, framealpha=0.92)
ax.set_title('no5 8 목표 순회 — 실제 궤적(f2t1, 10-14 15:21~15:31, 8/8 성공) · 원 = 목표(파랑 방향까지, 빨강 위치만) · 초록 삼각형 = 출발', fontsize=11, loc='left')
fig.savefig(out, dpi=130, bbox_inches='tight'); print('저장', out)
for tb, k in bounds: print('목표 %d %s 시작 %s' % (k, G[k - 1][3], time.strftime('%H:%M:%S', time.localtime(tb))))
print('끝', time.strftime('%H:%M:%S', time.localtime(tend)))
