# 10-02 §9.1: f2b4 복귀 때 상자가 카메라(D455 깊이 수평 화각 87° = ±43.5°) 안에 있었나 — 기하 계산만
#   카메라: base_link 기준 (0.234, 0.044), yaw −2.68°(URDF camera_joint). 상자: 10-01 §8.36 자리 x 1.15~1.25, y −0.17~0
#   거리 구간: 점군(전역 카메라 층) 0.45(근거리 제거)~1.2 m, nvblox 통합 ≤ 1.4 m
import numpy as np, math
L = np.load(r'f2a6\f2b4_lviz.npz', allow_pickle=True)['recs']
BOX = [(x, y) for x in np.linspace(1.15, 1.25, 3) for y in np.linspace(-0.17, 0.0, 4)]
CX, CY, CYAW, HF = 0.234, 0.044, -0.04677, math.radians(43.5)
rows = []
for r in L:
    X, Y, T = r['pose']; c, s = math.cos(T), math.sin(T)
    cx, cy, cyaw = X + c * CX - s * CY, Y + s * CX + c * CY, T + CYAW
    pts = []
    for bx, by in BOX:
        d = math.hypot(bx - cx, by - cy); a = (math.atan2(by - cy, bx - cx) - cyaw + math.pi) % (2 * math.pi) - math.pi
        pts.append((d, a))
    inf = [p for p in pts if abs(p[1]) <= HF]
    rows.append((r['t'], X, Y, math.degrees(T), len(inf), min(p[0] for p in pts), math.degrees(min(abs(p[1]) for p in pts)),
                 sum(1 for p in inf if 0.45 <= p[0] <= 1.2), sum(1 for p in inf if p[0] <= 1.4)))
print('  t   로버(x,y,θ)            | 화각 안 모서리점/12 | 최소 거리 | 최소 각 | 화각 안 & 0.45~1.2 m | 화각 안 & ≤1.4 m')
for r in rows:
    if r[0] >= 40: print('+%3.0f (%.2f,%.2f,%4.0f°) | %2d | %.2f m | %3.0f° | %2d | %2d' % r)
