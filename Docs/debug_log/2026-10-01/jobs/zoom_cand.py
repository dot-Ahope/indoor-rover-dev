import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from PIL import Image
plt.rcParams['font.family'] = 'Malgun Gothic'; plt.rcParams['axes.unicode_minus'] = False
exec(open('../render_cand.py', encoding='utf-8').read().split('def panel')[0])
rgb = np.full((H, W, 3), 0.93); rgb[(GA == 254) | (GB == 254)] = 1.0
oa, ob = GA == 0, GB == 0
rgb[oa & ~ob] = (0.12, 0.37, 0.82); rgb[ob & ~oa] = (0.86, 0.25, 0.05); rgb[oa & ob] = (0.1, 0.1, 0.1)
Z = [('출발 방·문', -2.5, 3.5, -1.5, 3.8), ('동쪽 방 동벽', 4.5, 7.5, -1.5, 3.8), ('남쪽 책상 구역', -3.5, 3, -7, -2.5), ('남동쪽', 3, 10, -7, -1)]
fig, axs = plt.subplots(1, 4, figsize=(24, 6.5), dpi=110)
for a, (t, xa, xb, ya, yb) in zip(axs, Z):
    a.imshow(rgb, extent=[x0, x0 + W * r, y0, y0 + H * r], interpolation='nearest'); a.set_xlim(xa, xb); a.set_ylim(ya, yb); a.set_title(t)
    a.set_xticks(np.arange(np.ceil(xa), xb, 0.5)); a.set_yticks(np.arange(np.ceil(ya), yb, 0.5)); a.grid(alpha=.35); a.tick_params(labelsize=7)
plt.suptitle('검정 = 둘 다 · 파랑 = office_v1 만 · 주황 = 후보만 (격자 0.5 m)'); plt.tight_layout(); plt.savefig('../cand_zoom.png')
