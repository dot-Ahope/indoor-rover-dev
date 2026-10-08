# 10-08 §3: 이번 순회 목표 10 개(저장 지도 office_v3 위) — 순서·이름·판정 방식, 지난 순회(10-07 f2c1+f2c2) 실제 궤적, 상자 위치
import numpy as np, math, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
plt.rcParams['font.family'] = 'Malgun Gothic'; plt.rcParams['axes.unicode_minus'] = False
Z = np.load('wi_f2d2.npz'); g = Z['map']; res, ox, oy = Z['meta']
img = np.where(g < 0, 0.75, np.where(g >= 50, 0.0, 1.0))
G = [(2.25, -1.6, 'B', 'p'), (-1.6, -2.0, '서쪽 문 앞', 'p'), (-1.65, -3.7, '서쪽 통로', 'p'), (-1.6, -5.5, '남서 구석', 'f'), (1.6, -5.55, 'D', 'p'),
     (-1.6, -5.5, '남서 구석', 'f'), (-1.65, -3.7, '서쪽 통로', 'p'), (-1.6, -2.1, '서쪽 문 앞(돌아올 때)', 'p'), (5.5, -2.2, 'W3(동쪽)', 'p'), (0.0, 0.0, '출발', 'p')]
fig, ax = plt.subplots(figsize=(13, 10), dpi=110)
ax.imshow(img, origin='lower', cmap='gray', vmin=0, vmax=1, extent=[ox, ox + g.shape[1] * res, oy, oy + g.shape[0] * res])
def traj(f):
    Z = np.load(f); mo, ob = Z['mo'], Z['ob']; out = []
    for t, x, y, th in ob[::10]:
        i = min(np.searchsorted(mo[:, 0], t), len(mo) - 1); mx, my, mth = mo[i, 1:]; c, s = math.cos(mth), math.sin(mth); out.append((mx + c * x - s * y, my + s * x + c * y))
    return np.array(out)
for f, lab in (('x913_f2c1.npz', '지난 순회 실제 궤적(10-07 f2c1+f2c2)'), ('x913_f2c2.npz', None)):
    T = traj(f); ax.plot(T[:, 0], T[:, 1], color='#4e98e2', lw=1.6, alpha=0.55, label=lab)
ax.plot(0, 0, marker='*', ms=20, color='#2e7d32', zorder=5); ax.annotate('출발 (0, 0)\n동쪽(→)을 보고 시작', (0, 0), xytext=(-1.4, 0.45), fontsize=10, color='#2e7d32', weight='bold')
for (x0, x1, y0, y1, lab) in ((1.3, 1.6, -0.45, -0.3, '상자 ①'), (1.1, 1.3, -0.1, 0.1, '상자 ②')):
    ax.add_patch(plt.Rectangle((x0, y0), x1 - x0, y1 - y0, color='#e67e22', alpha=0.85, zorder=4)); ax.text(x1 + 0.05, y0 - 0.12, lab, fontsize=9, color='#c0392b')
seen = {}
for i, (x, y, name, m) in enumerate(G):
    k = next((q for q in seen if abs(q[0] - x) < 0.3 and abs(q[1] - y) < 0.3), (x, y)); off = seen.get(k, 0); seen[k] = off + 1
    col = '#8e24aa' if m == 'f' else '#c62828'
    ax.plot(x, y, 'o', ms=13, mfc='white', mec=col, mew=2.5, zorder=6)
    ax.annotate('%d %s%s' % (i + 1, name, ' (위치만)' if m == 'f' else ''), (x, y), xytext=(x + 0.25, y + 0.25 - 0.38 * off), fontsize=10, weight='bold', color=col, zorder=7,
                bbox=dict(fc='white', ec=col, alpha=0.85, boxstyle='round,pad=0.2'))
ax.set_xlim(-3.2, 7.6); ax.set_ylim(-7.0, 2.0); ax.set_aspect('equal'); ax.grid(alpha=0.25); ax.legend(loc='upper right', fontsize=9)
ax.set_xlabel('map x (m)'); ax.set_ylabel('map y (m)')
ax.set_title('10-08 순회 목표 10 개(순서대로) — 빨강 = 경로 끝 방향으로 도착, 보라 = 위치만 판정(방향 맞춤 없음)', fontsize=11)
fig.savefig(r'F:\6_Indoor_Rover\Rover\Docs\04_navigation\figures\2026-10-08_patrol_goals.png', bbox_inches='tight'); print('ok')
