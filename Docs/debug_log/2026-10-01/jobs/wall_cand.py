# 10-01 §1: 두 방 사이 벽(줄자 ≈ 0.20 m) 두께와 출발 방 폭(줄자 1.97 m)을 후보·office_v1 에서 같은 방법(빈 셀→점유 셀 경계)으로
import numpy as np
exec(open('../render_cand.py', encoding='utf-8').read().split('def panel')[0])
def cell(x, y): return H - 1 - int((y - y0) / r), int((x - x0) / r)
def wall(G, y):  # x 2.3~3.8 사이 빈→점유→빈 : 점유 구간 폭(가운데 큰 덩어리)
    rr, c0 = cell(2.3, y); _, c1 = cell(3.8, y); row = G[rr, c0:c1]
    occ = np.where(row == 0)[0]
    if not len(occ): return float('nan')
    return (occ[-1] - occ[0] + 1) * r, x0 + (c0 + occ[0]) * r
def width(G, x):  # 출발 방: y -1.0~1.8 사이 빈 구간 최대 길이
    _, cc = cell(x, 0); r0, _ = cell(x, 1.8); r1, _ = cell(x, -1.0); col = G[r0:r1, cc] == 254
    best = cur = 0
    for v in col: cur = cur + 1 if v else 0; best = max(best, cur)
    return best * r
for n, G in (('office_v1', GA), ('후보', GB)):
    print('%-9s 벽 두께(y 0.5/1.0/2.0): %s | 출발 방 폭(x 0.0/0.5): %.2f / %.2f m' % (n, ' / '.join('%.2f m(시작 x %.2f)' % wall(G, y) for y in (0.5, 1.0, 2.0)), width(G, 0.0), width(G, 0.5)))
