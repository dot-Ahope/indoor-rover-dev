# 10-01 §1: office_v1 과 후보(cand_0930_cut699) 격자를 월드 좌표로 맞춰 겹쳐 그림 — 이중 벽(R2) 확인용
import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from PIL import Image
plt.rcParams['font.family'] = 'Malgun Gothic'
def load(n):
    im = np.array(Image.open(n + '.pgm')); y = {l.split(':')[0]: l.split(':', 1)[1].strip() for l in open(n + '.yaml') if ':' in l}
    o = [float(v) for v in y['origin'].strip('[]').split(',')]; return im, float(y['resolution']), o[0], o[1]
A, r, ax0, ay0 = load('office_v1'); B, _, bx0, by0 = load('cand_0930_cut699')
x0, y0 = min(ax0, bx0), min(ay0, by0); x1 = max(ax0 + A.shape[1] * r, bx0 + B.shape[1] * r); y1 = max(ay0 + A.shape[0] * r, by0 + B.shape[0] * r)
W, H = int(round((x1 - x0) / r)), int(round((y1 - y0) / r))
def place(im, ox, oy):
    g = np.full((H, W), 205, np.uint8); c = int(round((ox - x0) / r)); rr = H - int(round((oy - y0) / r)) - im.shape[0]
    g[rr:rr + im.shape[0], c:c + im.shape[1]] = im; return g
GA, GB = place(A, ax0, ay0), place(B, bx0, by0)
def panel(ax, G, title):
    rgb = np.full((H, W, 3), 0.80); rgb[G == 254] = 1.0; rgb[G == 0] = 0.08
    ax.imshow(rgb, extent=[x0, x0 + W * r, y0, y0 + H * r]); ax.set_title(title); ax.plot(0, 0, 'o', ms=7, mfc='none', mec='r', mew=2)
fig, axs = plt.subplots(1, 3, figsize=(22, 6.6), dpi=110)
panel(axs[0], GA, 'office_v1 (09-30 오전, 저장본)'); panel(axs[1], GB, '후보 cand_0930_cut699 (점프 3 s 전까지 재생)')
rgb = np.full((H, W, 3), 0.93); rgb[(GA == 254) | (GB == 254)] = 1.0
oa, ob = GA == 0, GB == 0
rgb[oa & ~ob] = (0.12, 0.37, 0.82); rgb[ob & ~oa] = (0.86, 0.25, 0.05); rgb[oa & ob] = (0.1, 0.1, 0.1)
axs[2].imshow(rgb, extent=[x0, x0 + W * r, y0, y0 + H * r]); axs[2].set_title('겹침: 검정 = 둘 다, 파랑 = office_v1 만, 주황 = 후보만'); axs[2].plot(0, 0, 'o', ms=7, mfc='none', mec='r', mew=2)
for a in axs: a.set_xticks(range(int(np.ceil(x0)), int(x1) + 1)); a.set_yticks(range(int(np.ceil(y0)), int(y1) + 1)); a.grid(alpha=.3); a.tick_params(labelsize=7)
plt.tight_layout(); plt.savefig('../cand_compare.png')
both = (oa & ob).sum(); print('점유 셀: v1 %d, 후보 %d, 겹침 %d (v1 의 %.0f %%), 후보만 %d' % (oa.sum(), ob.sum(), both, both / oa.sum() * 100, (ob & ~oa).sum()))
print('후보 크기 %.1f × %.1f m, 빈 셀 v1 %d → 후보 %d' % (B.shape[1] * r, B.shape[0] * r, (A == 254).sum(), (B == 254).sum()))
