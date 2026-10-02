# 10-02 §5: 지울 후보 묶음 번호 그림(3 칸 이상) + 병목 세 곳(점선 원)
import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from PIL import Image
from scipy import ndimage
plt.rcParams['font.family'] = 'Malgun Gothic'; plt.rcParams['axes.unicode_minus'] = False
SP = r'C:\Users\magma\AppData\Local\Temp\claude\F--6-Indoor-Rover-Rover\21d4aa9f-8412-4905-b23d-17554af330ea\scratchpad'
Z = np.load(SP + r'\clear_cand.npz'); im = np.array(Image.open(r'F:\6_Indoor_Rover\Rover\Docs\04_navigation\maps\office_v3.pgm')); H, W = im.shape
rgb = np.ones((H, W, 3)); rgb[(im != 0) & (im != 254)] = (0.9, 0.9, 0.9); rgb[im == 0] = (0.55, 0.55, 0.55); rgb[Z['solid']] = (0.1, 0.1, 0.1)
cand = Z['A'] | Z['B'] | Z['C']; rgb[Z['B']] = (0.93, 0.5, 0.1); rgb[Z['A'] | Z['C']] = (0.1, 0.65, 0.3)
lab, n = ndimage.label(cand, structure=np.ones((3, 3), bool)); sizes = ndimage.sum(cand, lab, range(1, n + 1))
order = np.argsort(-sizes); E = [-5.29, -5.29 + W * .05, -6.96, -6.96 + H * .05]
fig, ax = plt.subplots(figsize=(15, 10.5), dpi=100); ax.imshow(rgb, extent=E, interpolation='nearest')
q = 0
for k in order:
    if sizes[k] < 3: break
    q += 1; ii, jj = np.where(lab == k + 1); cx = -5.29 + (jj.mean() + .5) * .05; cy = -6.96 + (H - 1 - ii.mean() + .5) * .05
    ax.annotate('#%d' % q, (cx, cy), xytext=(cx + 0.25, cy + 0.25), fontsize=10, fontweight='bold', color='#b03a00', arrowprops=dict(arrowstyle='-', color='#b03a00', lw=.8))
for nm, (bx, by) in (('서 병목', (-1.64, -4.41)), ('가운데 병목', (0.96, -3.16)), ('동 병목', (3.31, -3.16))):
    ax.add_patch(plt.Circle((bx, by), 0.35, fill=False, ec='#2b6cb0', ls='--', lw=1.6)); ax.text(bx - 0.4, by - 0.6, nm, color='#2b6cb0', fontsize=9)
ax.set_xlim(-5.3, 9.0); ax.set_ylim(-7.0, 4.5); ax.grid(alpha=.25)
ax.set_title('office_v3 지울 후보 묶음(3 칸 이상, 번호 = 크기 순) — 주황 = 라이다만, 초록 = nvblox 도 비어 있음, 검정 = 확인된 벽(10-01 주행에서 라이다가 3 회 이상 맞춤), 회색 = 증거 부족', fontsize=10)
fig.tight_layout(); fig.savefig(r'F:\6_Indoor_Rover\Rover\Docs\04_navigation\figures\2026-10-02_clear_candidates.png'); print(q)
