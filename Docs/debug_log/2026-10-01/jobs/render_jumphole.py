# 10-01 §8.42: 점프 지점 주변 지도 구멍(미지 칸)과 점프 전·후 추정 자세
import numpy as np, matplotlib, math
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from PIL import Image
plt.rcParams['font.family'] = 'Malgun Gothic'; plt.rcParams['axes.unicode_minus'] = False
im = np.array(Image.open(r'F:\6_Indoor_Rover\Rover\Docs\04_navigation\maps\office_v2.pgm')); mox, moy = -5.29, -6.96; MH, MW = im.shape
rgb = np.ones((MH, MW, 3)); rgb[im == 0] = (0.12, 0.12, 0.12); rgb[(im != 0) & (im != 254)] = (0.95, 0.62, 0.25)
fig, ax = plt.subplots(figsize=(9, 4.6), dpi=110)
ax.imshow(rgb, extent=[mox, mox + MW * .05, moy, moy + MH * .05], interpolation='nearest')
FP = np.array([[0.262, 0.165], [0.262, -0.165], [-0.248, -0.165], [-0.248, 0.165], [0.262, 0.165]])
for (X, Y, T), col, lab in (((0.54, -5.62, math.radians(159)), '#2b6cb0', '점프 직전 추정 (실제와 일치)'), ((-0.83, -5.60, math.radians(169)), '#c53030', '점프 직후 추정 (틀림)')):
    c, s = math.cos(T), math.sin(T); ax.plot(X + c * FP[:, 0] - s * FP[:, 1], Y + s * FP[:, 0] + c * FP[:, 1], '-', color=col, lw=2.4, label=lab)
ax.annotate('', xy=(-0.6, -5.2), xytext=(0.4, -5.2), arrowprops=dict(arrowstyle='->', color='#c53030', lw=2.2))
ax.text(-0.45, -5.12, 'x 로만 -1.33 m', color='#c53030', fontsize=10, fontweight='bold')
ax.set_xlim(-2.4, 2.6); ax.set_ylim(-6.6, -4.2); ax.set_aspect('equal'); ax.grid(alpha=.25)
ax.plot([], [], 's', color=(0.95, 0.62, 0.25), label='지도 미지 칸(구멍)'); ax.legend(loc='upper right', fontsize=8, framealpha=.92)
ax.set_title('남쪽 통로: 곧은 남쪽 벽 외에 x 를 잡아 줄 특징이 적고, 점프 지점 옆에 미지 칸', fontsize=10)
fig.tight_layout(); fig.savefig('jump_hole.png')
