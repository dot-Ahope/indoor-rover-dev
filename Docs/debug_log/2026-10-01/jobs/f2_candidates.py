# 10-01 §8: F2 웨이포인트 후보 — office_v2 격자에서 각 후보의 벽까지 여유(가장 가까운 점유 셀 거리)와 미지 비율, 그림
import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from PIL import Image
from scipy import ndimage
plt.rcParams['font.family'] = 'Malgun Gothic'; plt.rcParams['axes.unicode_minus'] = False
im = np.array(Image.open('Docs/04_navigation/maps/office_v2.pgm')); r = 0.05; ox, oy = -5.29, -6.96; H, W = im.shape
dist = ndimage.distance_transform_edt(im != 0) * r
def rc(x, y): return H - 1 - int((y - oy) / r), int((x - ox) / r)
C = [('S 출발·복귀', 0.0, 0.0), ('B 문 밖', 2.25, -1.6), ('C 서쪽 책상 구역', -1.6, -2.0), ('D 남쪽 통로', 1.6, -5.55), ('W3 (F0-b 목표, 전선)', 5.5, -2.2)]
rgb = np.full((H, W, 3), 0.80); rgb[im == 254] = 1.0; rgb[im == 0] = 0.08
fig, ax = plt.subplots(figsize=(13, 9), dpi=100)
ax.imshow(rgb, extent=[ox, ox + W * r, oy, oy + H * r], interpolation='nearest')
for n, x, y in C:
    i, j = rc(x, y); d = dist[i, j]; st = {0: '점유', 254: '빈 곳', 205: '미지'}.get(int(im[i, j]), str(im[i, j]))
    print('%-22s (%+.2f, %+.2f) 셀 %s, 벽까지 %.2f m' % (n, x, y, st, d))
    ax.plot(x, y, 'o', ms=10, mfc='none', mec='#d62', mew=2.5); ax.text(x + 0.15, y + 0.15, '%s\n여유 %.2f m' % (n, d), fontsize=9, color='#a31', bbox=dict(fc='white', ec='none', alpha=.75, pad=1))
ax.arrow(0, 0, 0.4, 0, color='r', width=0.03)
R = [(0,0),(2.25,-1.6),(-1.6,-2.0),(1.6,-5.55),(5.5,-2.2),(0,0)]
for k,((x1,y1),(x2,y2)) in enumerate(zip(R,R[1:])): ax.annotate('', xy=(x2,y2), xytext=(x1,y1), arrowprops=dict(arrowstyle='->', color='#36c', lw=1.6, ls='--')); ax.text((x1+x2)/2, (y1+y2)/2, str(k+1), color='#36c', fontsize=11, fontweight='bold')
ax.plot([1.85, 2.65], [-0.65, -0.65], color='g', lw=4); ax.text(2.7, -0.55, '문', color='g')
ax.set_xticks(range(-5, 12)); ax.set_yticks(range(-7, 5)); ax.grid(alpha=.3)
ax.set_title('F2 웨이포인트 순회안 (office_v2) — 순서 1→5, 파란 점선은 순서만(실제 경로는 NavFn 이 계획) — 여유 = 가장 가까운 점유 셀까지')
plt.tight_layout(); plt.savefig('Docs/04_navigation/figures/2026-10-01_f2_candidates.png')
