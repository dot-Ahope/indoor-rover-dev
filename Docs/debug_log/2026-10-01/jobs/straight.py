# 10-01 §2.2: 책상 구역 남쪽 벽은 실제로 일직선(사용자) — 각 지도에서 벽 점(열마다 y −5.9 아래 첫 점유)을 x −2.0~6.0 에서 모아
#   직선 맞춤 뒤 벗어남. 의자 등 튀는 점은 중앙값 기준 ±0.4 m 밖이면 제외.
import numpy as np, os
exec(open('../render_cand.py', encoding='utf-8').read().split('def panel')[0])
def cell(x, y): return H - 1 - int((y - y0) / r), int((x - x0) / r)
def pts(G):
    P = []
    for x in np.arange(-2.0, 6.0, r):
        rr, cc = cell(x, -5.9)
        for k in range(rr, H):
            if G[k, cc] == 0: P.append((x, y0 + (H - 1 - k) * r)); break
    P = np.array(P); m = np.median(P[:, 1]); return P[np.abs(P[:, 1] - m) < 0.4]
for n, G in (('office_v1', GA), (os.environ.get('CAND'), GB)):
    P = pts(G); k, b = np.polyfit(P[:, 0], P[:, 1], 1); res = P[:, 1] - (k * P[:, 0] + b)
    seg = [P[(P[:, 0] >= a) & (P[:, 0] < a + 2), 1].mean() for a in (-2, 0, 2, 4)]
    print('%-24s 점 %3d | 기울기 %+.1f°(8 m 에 %+.2f m) | 직선 벗어남 σ %.3f, 최대 %.2f m | 2 m 구간 평균 y: %s' % (
        n, len(P), np.degrees(np.arctan(k)), k * 8, res.std(), np.abs(res).max(), ' '.join('%+.2f' % s for s in seg)))
