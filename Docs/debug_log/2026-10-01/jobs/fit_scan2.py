# 10-01 §8.40: 국소(±0.3 m, ±4°) 격자 탐색 — 책상 반복 구조 때문에 Powell 이 1.3~2.7 m 옆 칸으로 빠지는 것(fit_scan.py) 방지
import numpy as np, math
from fit_scan import cost
def fit_local(rec, R=0.30):
    sc = rec['scan'].astype(float); X, Y, _ = rec['pose']; sc = sc[np.hypot(sc[:, 0] - X, sc[:, 1] - Y) < 4.0]
    best = (cost([0, 0, 0], sc, X, Y), 0, 0, 0)
    for th in np.radians(np.arange(-4, 4.01, 1)):
        for dx in np.arange(-R, R + 1e-9, 0.02):
            for dy in np.arange(-R, R + 1e-9, 0.02):
                c = cost([dx, dy, th], sc, X, Y)
                if c < best[0]: best = (c, dx, dy, th)
    return cost([0, 0, 0], sc, X, Y) ** .5, best[0] ** .5, best[1:]
if __name__ == '__main__':
    for f, ks in ((r'f2a6/f2a12_lviz.npz', (0, 10, 30, 45)), (r'f2a6/f2a12_g34.npz', (0, 30, 50, 60, 70, 80, 90))):
        R = np.load(f, allow_pickle=True)['recs']; print('==', f)
        for k in ks:
            r = R[k]; e0, e1, (dx, dy, th) = fit_local(r)
            print('  t%5.1f 자세 (%.2f, %.2f, %4.0f°) 잔차 %.3f → %.3f m | 보정 dx %+.2f dy %+.2f dθ %+.0f°' % (r['t'], *r['pose'][:2], math.degrees(r['pose'][2]), e0, e1, dx, dy, math.degrees(th)))
