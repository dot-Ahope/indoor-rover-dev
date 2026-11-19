#!/usr/bin/env python3
"""fig_stop_costmap — 로버가 멈춘 순간의 로컬 코스트맵·차체 풋프린트·라이다 점을 겹쳐 그리고, 풋프린트에 걸린 비용과 실제 여유(라이다)를 수치로 낸다. (2026-10-13)
  왜: f2o1 목표 3 이 "후보 궤적 전부 충돌"로 중단됐는데 사용자 확인으로는 상자에 닿지 않았다 → 코스트맵이 본 것과 라이다가 본 실제 거리를 견준다.
  입력: bag(/local_costmap/costmap, /scan, /tf, /tf_static). 코스트맵 값은 OccupancyGrid 환산값(100 = 치명 254, 99 = 내접 253, 그 아래 = 감쇠 비용).
  출력: 그림(왼쪽 = 지정 시각의 코스트맵 + 풋프린트 + 라이다 점, 오른쪽 = 그 전 구간의 풋프린트 둘레 최대 비용·라이다 최소 여유 시간열) + 표.
  사용: fig_stop_costmap.py bag 출력.png HH:MM:SS [앞으로 볼 초=25]"""
import sys, time, math
from pathlib import Path
import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
sys.path.insert(0, str(Path(__file__).resolve().parent)); import lib_rover as L   # 11-19 §3: 읽기 · 변환 · 여유 계산은 lib_rover(표본 = 가장 가까운 것, 옛 규칙 그대로)
plt.rcParams['font.family'] = 'Malgun Gothic'; plt.rcParams['axes.unicode_minus'] = False
bag, out, hms = sys.argv[1], sys.argv[2], sys.argv[3]; BACK = float(sys.argv[4]) if len(sys.argv) > 4 else 25.0
FP = L.FP; PAD = 0.01   # nav2_params.yaml footprint + footprint_padding
FPP = FP + np.sign(FP) * PAD
Dg = L.read_bag(bag, ['/tf', '/local_costmap/costmap', '/scan'], hms, hms, pre=BACK + 2, post=8.0)
tgt = Dg['tA']; fr0 = Dg.get('loc_frame', 'odom')
odom = Dg['ob']; grids = [g + (fr0,) for g in Dg['loc']]; scans = Dg['scan']
def chain(frame): return L.chain(Dg['static'], frame)
def pose(ts): return L.nearest(odom, ts)[1]
fp_world = L.w2
def edge_pts(P, step=0.01):
    o = []
    for i in range(len(P)):
        a, b = P[i], P[(i + 1) % len(P)]; n = max(int(np.linalg.norm(b - a) / step), 1); o.append(a + (b - a) * np.linspace(0, 1, n, endpoint=False)[:, None])
    return np.vstack(o)
def clearance(pts_base):   # 차체(패딩 없는 실제 풋프린트) 바깥 점까지의 최소 거리와 그 점
    d = L.rect_clear(pts_base); i = int(np.argmin(d)); return d[i], pts_base[i, :2]


rows = []
for ts, ox, oy, res, G, fr in grids:
    if ts < tgt - BACK or ts > tgt + 6: continue
    M = pose(ts); E = fp_world(M, edge_pts(FPP)); ij = np.c_[((E[:, 1] - oy) / res).astype(int), ((E[:, 0] - ox) / res).astype(int)]
    ok = (ij[:, 0] >= 0) & (ij[:, 0] < G.shape[0]) & (ij[:, 1] >= 0) & (ij[:, 1] < G.shape[1]); v = G[ij[ok, 0], ij[ok, 1]]
    k = int(np.argmin([abs(s[0] - ts) for s in scans])); S = scans[k]; pb = L.w2(chain(S[1]), S[2]); d, p = clearance(pb)
    Lb = L.w2(np.linalg.inv(M), L.lethal_cells((ts, ox, oy, res, G)))
    near = Lb[(np.abs(Lb[:, 0]) < 1.0) & (np.abs(Lb[:, 1]) < 1.0)]; dl, pl = clearance(near) if len(near) else (float('nan'), np.array([0, 0]))   # 치명 칸 중심까지(칸 반폭 2.5 cm 는 빼지 않음)
    rows.append((ts, int(v.max()), int((v >= 100).sum()), d, p, math.atan2(M[1, 0], M[0, 0]), M[0, 3], M[1, 3], dl, pl))
print('시각        둘레 최대 비용  라이다 최소 여유(m)·그 점(차체 기준 x 앞, y 왼쪽)   코스트맵 치명 칸 중심까지 차체 여유(m)·그 칸')
for r in rows: print('%s.%d      %3d          %.3f (%.2f, %.2f)                        %.3f (%.2f, %.2f)' % (time.strftime('%H:%M:%S', time.localtime(r[0])), int(r[0] % 1 * 10), r[1], r[3], r[4][0], r[4][1], r[8], r[9][0], r[9][1]))

g = min(grids, key=lambda g_: abs(g_[0] - tgt)); ts, ox, oy, res, G, fr = g; M = pose(ts); cx, cy = M[0, 3], M[1, 3]
fig, (ax, ax2) = plt.subplots(1, 2, figsize=(14, 6.2), gridspec_kw=dict(width_ratios=[1.15, 1]))
ext = (ox, ox + G.shape[1] * res, oy, oy + G.shape[0] * res)
im = ax.imshow(np.where(G < 0, 0, G), origin='lower', extent=ext, cmap='Greys', vmin=0, vmax=100, interpolation='nearest')
leth = np.argwhere(G >= 100); ax.scatter(ox + (leth[:, 1] + 0.5) * res, oy + (leth[:, 0] + 0.5) * res, s=22, marker='s', color='#b2182b', label='치명 칸(100)', zorder=2)
ins = np.argwhere(G == 99); ax.scatter(ox + (ins[:, 1] + 0.5) * res, oy + (ins[:, 0] + 0.5) * res, s=22, marker='s', color='#f4a582', label='내접 칸(99)', zorder=2)
k = int(np.argmin([abs(s[0] - ts) for s in scans])); S = scans[k]; pw = L.w2(M @ chain(S[1]), S[2])
ax.scatter(pw[:, 0], pw[:, 1], s=5, color='#2166ac', label='라이다 점', zorder=4)
for P, st, lb in ((FP, '-', '차체(0.51 × 0.33 m)'), (FPP, '--', '풋프린트(+패딩 1 cm)')):
    W = fp_world(M, P); ax.plot(*np.r_[W, W[:1]].T, st, color='#1b7837', lw=1.8, label=lb, zorder=5)
h = fp_world(M, np.array([[0, 0], [0.262, 0]])); ax.annotate('', xy=h[1], xytext=h[0], arrowprops=dict(arrowstyle='->', color='#1b7837', lw=1.6), zorder=6)
ax.set_xlim(cx - 0.9, cx + 0.9); ax.set_ylim(cy - 0.9, cy + 0.9); ax.set_aspect('equal'); ax.grid(color='#ccc', lw=0.3)
ax.set_xlabel('%s x (m)' % fr); ax.set_ylabel('%s y (m)' % fr); ax.legend(fontsize=8, loc='upper right', framealpha=0.9)
ax.set_title('%s 로컬 코스트맵(회색 = 감쇠 비용) — 화살표가 로버 앞' % time.strftime('%H:%M:%S', time.localtime(ts)), fontsize=11, loc='left')
R = np.array([(r[0] - tgt, r[1], r[3] * 100) for r in rows])
ax2.plot(R[:, 0], R[:, 1], '-o', ms=3, color='#b2182b'); ax2.axhline(100, color='#b2182b', lw=0.7, ls=':'); ax2.axhline(99, color='#f4a582', lw=0.7, ls=':')
ax2.set_ylabel('풋프린트 둘레 최대 비용 (100 = 치명, 99 = 내접)', color='#b2182b', fontsize=9); ax2.set_ylim(0, 105); ax2.set_xlabel('지정 시각 %s 기준 (s)' % hms); ax2.grid(color='#ddd', lw=0.4)
ax2.set_title('멈추기까지: 코스트맵이 본 비용(위) · 라이다가 본 실제 여유(아래)', fontsize=11, loc='left')
ax3 = ax2.inset_axes([0, -0.62, 1, 0.45]); ax3.plot(R[:, 0], R[:, 2], '-o', ms=3, color='#2166ac'); ax3.set_ylabel('라이다 최소 여유 (cm)', color='#2166ac', fontsize=9); ax3.set_ylim(0, max(30, R[:, 2].max() * 1.1)); ax3.grid(color='#ddd', lw=0.4); ax3.set_xlim(ax2.get_xlim())
fig.savefig(out, dpi=130, bbox_inches='tight'); print('저장', out)
