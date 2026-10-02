# 10-02 §1: office_v2 vs 후보(cand_1002_f2a12_c276_nolc) — 남쪽 통로 구멍이 메워졌나, 옛 벽이 움직였나
import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from PIL import Image
plt.rcParams['font.family'] = 'Malgun Gothic'; plt.rcParams['axes.unicode_minus'] = False
M = r'F:\6_Indoor_Rover\Rover\Docs\04_navigation\maps'
ox, oy = -5.29, -6.96
def rgb(im):
    c = np.ones(im.shape + (3,)); c[im == 0] = (0.12, 0.12, 0.12); c[(im != 0) & (im != 254)] = (0.95, 0.62, 0.25); return c
a = np.array(Image.open(M + r'\office_v2.pgm')); b = np.array(Image.open('cand_1002_f2a12_c276_nolc.pgm'))
ext = lambda im: [ox, ox + im.shape[1] * .05, oy, oy + im.shape[0] * .05]
# 겹침: 같은 원점(왼쪽 아래) 기준으로 아래 행을 맞춤
H = a.shape[0]; bb = b[b.shape[0] - H:, :]
ov = np.ones(a.shape + (3,)); both = (a == 0) & (bb == 0); ov[both] = (0.12, 0.12, 0.12); ov[(a == 0) & ~both] = (0.17, 0.42, 0.69); ov[(bb == 0) & ~both] = (0.75, 0.34, 0.13)
ov[(a != 0) & (a != 254) & (bb == 254)] = (0.55, 0.85, 0.6)
fig, ax = plt.subplots(3, 1, figsize=(10, 11.5), dpi=100)
for k, (im, t, e) in enumerate(((a, 'office_v2 — 주황 = 미지(구멍)', ext(a)), (b, '후보 cand_1002_f2a12_c276_nolc (f2a12 +276 s 까지 이어 그림, 루프 클로저 끔)', ext(b)), (ov, '겹침 — 검정 둘 다 벽, 파랑 v2 만 벽, 주황 후보만 벽, 연두 = 구멍이 새로 비어 있음으로 확인된 칸', ext(a)))):
    ax[k].imshow(rgb(im) if k < 2 else im, extent=e, interpolation='nearest'); ax[k].set_xlim(-2.4, 4.0); ax[k].set_ylim(-6.6, -4.2); ax[k].set_aspect('equal'); ax[k].grid(alpha=.25); ax[k].set_title(t, fontsize=10)
    ax[k].plot(0.54, -5.62, 'o', ms=10, mfc='none', mec='#c53030', mew=2)
ax[0].text(0.62, -5.5, '점프 지점', color='#c53030', fontsize=9)
fig.tight_layout(); fig.savefig(r'F:\6_Indoor_Rover\Rover\Docs\04_navigation\figures\2026-10-02_hole_fill.png'); print('ok')
