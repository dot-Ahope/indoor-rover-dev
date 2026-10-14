#!/usr/bin/env python3
"""fig_patrol_goals — 순회 코스의 목표 지점을 저장 지도(office_v3) 위에 순서대로 그린다. (2026-10-14)
  왜: 10 개 목표 순회 전에 사용자가 어디를 뺄지 고르기 위해. 목표 좌표는 PC 러너(run_f2c.sh)의 FULL/FULLF 문자열과 같다(지도 절대 좌표, GOAL_FRAME=map).
  그림: 회색 = 저장 지도(검정 = 벽·물체), 번호 원 = 목표(빨강 = 위치만 맞춤 'f', 파랑 = 방향까지 'p'), 선 = 목표 사이 순서(직선 — 실제 경로가 아님).
        같은 자리를 두 번 가는 목표는 번호를 함께 적는다. 초록 삼각형 = 출발(0, 0, 방향 0° — 목표 10 과 같은 자리라 옆에 그림).
  사용: fig_patrol_goals.py 출력.png"""
import sys, math
import numpy as np, matplotlib, yaml
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from PIL import Image
plt.rcParams['font.family'] = 'Malgun Gothic'; plt.rcParams['axes.unicode_minus'] = False
out = sys.argv[1]
Y = yaml.safe_load(open('Docs/04_navigation/maps/office_v3.yaml', encoding='utf-8')); img = np.array(Image.open('Docs/04_navigation/maps/office_v3.pgm')); res = Y['resolution']; ox, oy = Y['origin'][:2]
H, W = img.shape; ext = (ox, ox + W * res, oy, oy + H * res)
# 10-08 FULLF(run_f2c.sh) — 이름은 10-01 §8 코스 정의(C · 위 복도 · W3). 10-14 §27.2: 10-02 이후 C 를 'W3' 로 잘못 부른 것을 되돌림
G = [(2.25, -1.6, 'p', 'B'), (-1.6, -2.0, 'p', 'C'), (-1.65, -3.7, 'p', '서쪽 통로'), (-1.6, -5.5, 'f', '남서'), (1.6, -5.55, 'p', 'D'),
     (-1.6, -5.5, 'f', '남서'), (-1.65, -3.7, 'p', '서쪽 통로'), (-1.6, -2.1, 'p', '위 복도'), (5.5, -2.2, 'p', 'W3'), (0.0, 0.0, 'p', '출발점 복귀')]
fig, ax = plt.subplots(figsize=(11, 9.5))
ax.imshow(np.flipud(img), origin='lower', extent=ext, cmap='gray', vmin=0, vmax=255, interpolation='nearest')
pts = np.array([[0.0, 0.0]] + [[g[0], g[1]] for g in G])
for k in range(len(pts) - 1):
    a, b = pts[k], pts[k + 1]; ax.annotate('', xy=b, xytext=a, arrowprops=dict(arrowstyle='->', color='#7b3294', lw=1.3, alpha=0.75, shrinkA=10, shrinkB=12))
groups = []   # 0.15 m 안의 목표는 한 원으로(2·8 은 0.1 m 차이)
for i, (x, y, m, nm) in enumerate(G, 1):
    for gr in groups:
        if math.hypot(gr[0][1] - x, gr[0][2] - y) < 0.15: gr.append((i, x, y, m, nm)); break
    else: groups.append([(i, x, y, m, nm)])
for gr in groups:
    x, y, m = gr[0][1], gr[0][2], gr[0][3]; col = '#c53030' if m == 'f' else '#2b6cb0'
    ax.scatter([x], [y], s=560, color=col, edgecolors='white', linewidths=1.8, zorder=5)
    ax.text(x, y, '·'.join(str(g[0]) for g in gr), color='white', fontsize=11 if len(gr) == 1 else 9, fontweight='bold', ha='center', va='center', zorder=6)
    lab = ' / '.join(sorted({'%s (%.2f, %.2f)' % (g[4], g[1], g[2]) for g in gr}, key=lambda q: q)) + (' · 위치만' if m == 'f' else '')
    ax.text(x + 0.28, y + 0.25, lab, fontsize=10, color='#1d2329', zorder=6, bbox=dict(boxstyle='round,pad=0.2', fc='white', ec='none', alpha=0.88))
ax.scatter([-0.35], [0], marker='>', s=200, color='#2f855a', zorder=7); ax.text(-0.75, 0.25, '출발', fontsize=10, color='#2f855a', fontweight='bold', zorder=7, bbox=dict(boxstyle='round,pad=0.2', fc='white', ec='none', alpha=0.88))
xs, ys = pts[:, 0], pts[:, 1]; ax.set_xlim(xs.min() - 1.2, xs.max() + 1.5); ax.set_ylim(ys.min() - 1.0, ys.max() + 1.0); ax.set_aspect('equal')
ax.set_xlabel('map x (m)'); ax.set_ylabel('map y (m)'); ax.grid(color='#9aa5ae', lw=0.3, alpha=0.5)
ax.set_title('10 개 목표 순회(10-08 FULLF) — 번호 = 가는 순서, 빨강 = 위치만 맞춤, 파랑 = 방향까지, 화살표 = 순서(실제 경로 아님)', fontsize=11, loc='left')
fig.savefig(out, dpi=130, bbox_inches='tight'); print('저장', out)
for i, (x, y, m, nm) in enumerate(G, 1): print('%2d  %-8s (%5.2f, %5.2f)  %s' % (i, nm, x, y, '위치만' if m == 'f' else '방향까지'))
