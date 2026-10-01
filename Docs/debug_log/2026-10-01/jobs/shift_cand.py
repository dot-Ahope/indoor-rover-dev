# 10-01 §1: 영역별로 후보를 office_v1 에 가장 잘 겹치는 평행 이동(±0.30 m, 5 cm 단위) — 두 지도가 어디서 얼마나 어긋났나
import numpy as np
from PIL import Image
exec(open('../render_cand.py', encoding='utf-8').read().split('def panel')[0])
oa, ob = (GA == 0).astype(float), (GB == 0).astype(float)
def cell(x, y): return H - 1 - int((y - y0) / r), int((x - x0) / r)
Z = [('출발 방', -1.5, 3.2, -1.0, 3.8), ('동쪽 방', 3.0, 6.5, -1.0, 3.8), ('남쪽 책상 구역', -3.5, 3.0, -6.6, -2.5), ('남동쪽', 3.0, 9.5, -6.6, -1.0)]
for t, xa, xb, ya, yb in Z:
    r0, c0 = cell(xa, yb); r1, c1 = cell(xb, ya); best = None
    for dy in range(-6, 7):
        for dx in range(-6, 7):
            a = oa[r0:r1, c0:c1]; b = ob[r0 + dy:r1 + dy, c0 + dx:c1 + dx]; s = (a * b).sum() / max(1, min(a.sum(), b.sum()))
            if best is None or s > best[0]: best = (s, dx, dy)
    a = oa[r0:r1, c0:c1]; b = ob[r0:r1, c0:c1]; s0 = (a * b).sum() / max(1, min(a.sum(), b.sum()))
    print('%-8s 그대로 겹침 %.0f %% | 최적 이동 x %+.2f m, y %+.2f m 에서 %.0f %%' % (t, s0 * 100, best[1] * r, -best[2] * r, best[0] * 100))
