# 10-02 §5: 지울 후보 그림 — 회색 = 지도 점유(증거 부족), 검정 = 확인된 벽(라이다 hit ≥ 3), 주황 = 후보 B(라이다만), 초록 = A(라이다+nvblox)
import numpy as np, matplotlib, sys
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from PIL import Image
plt.rcParams['font.family'] = 'Malgun Gothic'; plt.rcParams['axes.unicode_minus'] = False
SP = r'C:\Users\magma\AppData\Local\Temp\claude\F--6-Indoor-Rover-Rover\21d4aa9f-8412-4905-b23d-17554af330ea\scratchpad'
Z = np.load(SP + r'\clear_cand.npz'); im = np.array(Image.open(r'F:\6_Indoor_Rover\Rover\Docs\04_navigation\maps\office_v3.pgm')); H, W = im.shape
rgb = np.ones((H, W, 3)); rgb[(im != 0) & (im != 254)] = (0.9, 0.9, 0.9); rgb[im == 0] = (0.6, 0.6, 0.6); rgb[Z['solid']] = (0.1, 0.1, 0.1)
rgb[Z['B']] = (0.93, 0.55, 0.15); rgb[Z['A']] = (0.15, 0.65, 0.3)
pc = np.log10(1 + Z['pas'])
fig, ax = plt.subplots(1, 2, figsize=(17, 6.6), dpi=95)
E = [-5.29, -5.29 + W * .05, -6.96, -6.96 + H * .05]
ax[0].imshow(rgb, extent=E, interpolation='nearest'); ax[0].set_title('지울 후보: 주황 = 라이다만, 초록 = 라이다+nvblox, 검정 = 확인된 벽, 회색 = 증거 부족 점유', fontsize=10)
m = ax[1].imshow(np.where(pc > 0, pc, np.nan), extent=E, interpolation='nearest', cmap='viridis'); ax[1].set_title('라이다 통과 횟수(log10) — 어디를 봤나', fontsize=10); plt.colorbar(m, ax=ax[1], fraction=.03)
ax[1].contour(np.flipud(im == 0), levels=[0.5], extent=E, colors='r', linewidths=.4)
for a in ax: a.grid(alpha=.25)
fig.tight_layout(); fig.savefig(SP + r'\cand_clear.png'); print('ok')
