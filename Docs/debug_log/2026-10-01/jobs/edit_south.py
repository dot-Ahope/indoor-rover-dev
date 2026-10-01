# 10-01 §3: 사용자 지시 — 후보(루프 클로저 끔)의 책상 구역 남쪽 벽을 x ≥ 0 에서 office_v1 값에 맞춰 보정(격자 pgm 편집).
#   규칙: x ≥ 0 이고 v1 이 덮는 열에서, 띠 y ≤ Y_TOP 의 셀을 v1 셀로 바꾼다(v1 이 미지면 미지) → 휜 벽(후보)은 지우고 곧은 벽(v1)을 넣는다.
#   Y_TOP = −5.95: 두 지도 벽 점이 모두 −6.0 아래(§2.2), 책상 줄(≥ −5.5)은 건드리지 않음.
#   포즈 그래프(.posegraph)는 그대로 — 이 편집은 격자 지도(Nav2·AMCL 용)에만 적용된다.
import numpy as np, os
from PIL import Image
os.environ['CAND'] = 'cand_0930_cut699_nolc'
exec(open('../render_cand.py', encoding='utf-8').read().split('def panel')[0])
Y_TOP, X_FROM = -5.95, 0.0
x_v1_end = ax0 + A.shape[1] * r
cols = np.arange(W); rows = np.arange(H)
xs = x0 + (cols + 0.5) * r; ys = y0 + (H - 1 - rows + 0.5) * r
M = (ys[:, None] <= Y_TOP) & (xs[None, :] >= X_FROM) & (xs[None, :] < x_v1_end)
E = GB.copy(); E[M] = GA[M]
ch = (E != GB) & M
print('바뀐 셀 %d (점유→다른 것 %d, 다른 것→점유 %d), 범위 x %.2f~%.2f, y ≤ %.2f' % (ch.sum(), ((GB == 0) & ch).sum(), ((E == 0) & ch).sum(), X_FROM, x_v1_end, Y_TOP))
# 후보 원래 틀로 잘라 저장
c0 = int(round((bx0 - x0) / r)); r0 = H - int(round((by0 - y0) / r)) - B.shape[0]
out = E[r0:r0 + B.shape[0], c0:c0 + B.shape[1]]
N = 'cand_0930_cut699_nolc_s'
Image.fromarray(out).save(N + '.pgm')
open(N + '.yaml', 'w').write(open('cand_0930_cut699_nolc.yaml').read().replace('cand_0930_cut699_nolc.pgm', N + '.pgm'))
print('저장', N, out.shape)
