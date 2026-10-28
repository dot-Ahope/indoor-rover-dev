#!/usr/bin/env python3
"""fig_gcm_reach — 전역 코스트맵 덤프(chk_costmap_dump.py)에서 로버 칸부터 지나갈 수 있는 칸(값 ≤ 98, 미지 포함)을 넓이 우선으로 칠해
  어디서 막혔는지 본다(10-28 §16, PC). NavFn 은 내접(99) · 치명(100) 칸을 못 지나간다고 보고 그 기준으로 칠함(근사).
  인자: npz 출력.png [장소 x,y 여러 개 '이름:x:y']"""
import sys, collections, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
plt.rcParams.update({'font.family': 'Malgun Gothic', 'axes.unicode_minus': False})
D = np.load(sys.argv[1]); g = D['global_costmap_costmap']; ox, oy, r = D['global_costmap_costmap_o']; R = D['robot']
H, W = g.shape; ok = g <= 98   # 미지(−1)도 지나감
s = (int((R[1] - oy) / r), int((R[0] - ox) / r)); seen = np.zeros_like(ok); q = collections.deque([s]); seen[s] = True
while q:
    j, i = q.popleft()
    for dj, di in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        a, b = j + dj, i + di
        if 0 <= a < H and 0 <= b < W and ok[a, b] and not seen[a, b]: seen[a, b] = True; q.append((a, b))
img = np.ones((H, W, 3)); img[g == -1] = 0.85; img[(g >= 1) & (g <= 98)] = (0.93, 0.93, 0.90); img[seen] = (0.80, 0.93, 0.84)
img[g == 99] = (0.98, 0.72, 0.35); img[g >= 100] = (0.78, 0.12, 0.12)
m = D['map']; mo = D['map_o']
fig, ax = plt.subplots(figsize=(11, 8.5))
ax.imshow(img, origin='lower', extent=[ox, ox + W * r, oy, oy + H * r], interpolation='nearest')
yy, xx = np.nonzero(m >= 65); ax.scatter(mo[0] + (xx + .5) * mo[2], mo[1] + (yy + .5) * mo[2], s=0.6, c='k', alpha=0.6, label='정적 /map 점유')
ax.plot(R[0], R[1], 'o', ms=9, mfc='white', mec='k', mew=2); ax.annotate('로버', (R[0], R[1]), xytext=(6, 6), textcoords='offset points')
print('로버 칸', g[s], '· 닿는 칸 %d (%.1f m²)' % (seen.sum(), seen.sum() * r * r))
for t in sys.argv[3:]:
    nm, x, y = t.split(':'); x, y = float(x), float(y); c = (int((y - oy) / r), int((x - ox) / r))
    reach = bool(seen[c]); ax.plot(x, y, 'D', ms=7, mfc='white' if reach else 'red', mec='k'); ax.annotate(nm, (x, y), xytext=(6, -10), textcoords='offset points')
    print('  %s (%.2f, %.2f) 칸 %d · 닿음 %s' % (nm, x, y, g[c], reach))
ax.set_xlim(R[0] - 3.5, R[0] + 6.5); ax.set_ylim(R[1] - 6.2, R[1] + 1.8); ax.set_aspect('equal')
ax.set_title('전역 코스트맵 · 로버에서 닿는 칸(연초록) · 빨강 = 치명 100 · 주황 = 내접 99 · 회색 = 미지', loc='left', fontsize=11)
ax.legend(loc='lower right', markerscale=8, fontsize=9); fig.tight_layout(); fig.savefig(sys.argv[2], dpi=100)
