# 10-01 §2: 남쪽 벽 위치 — 출발 방 남쪽 벽(y≈−0.6, 문 쪽 벽 바깥 면)에서 남쪽 벽까지 거리를 x 별로(빈 셀 따라 아래로 첫 점유)
import numpy as np, os
exec(open('../render_cand.py', encoding='utf-8').read().split('def panel')[0])
def cell(x, y): return H - 1 - int((y - y0) / r), int((x - x0) / r)
def first_occ_down(G, x, ys):
    rr, cc = cell(x, ys)
    for k in range(rr, H):
        if G[k, cc] == 0: return y0 + (H - 1 - k) * r
    return float('nan')
print('x     | 남쪽 벽 y: office_v1  후보  차(후보−v1)')
for x in (-1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0, 3.5, 4.0, 4.5, 5.0):
    a, b = first_occ_down(GA, x, -5.6), first_occ_down(GB, x, -5.6)
    print('%+5.1f | %+.2f  %+.2f  %+.2f' % (x, a, b, b - a))
