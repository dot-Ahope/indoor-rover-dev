# 10-01 §8.40: 기록된 로버 자세가 맞는지 — 라이다 스캔(그 자세로 map 에 놓은 것)을 저장 지도 벽에 맞추는 데 필요한 보정(dx, dy, dθ)
import numpy as np, math, sys
from PIL import Image
from scipy import ndimage, optimize
im = np.array(Image.open(r'F:\6_Indoor_Rover\Rover\Docs\04_navigation\maps\office_v2.pgm')); MH, MW = im.shape
dt = ndimage.distance_transform_edt(im != 0) * 0.05
def cost(p, sc, X, Y):
    dx, dy, dth = p; c, s = math.cos(dth), math.sin(dth); x = X + dx + c * (sc[:, 0] - X) - s * (sc[:, 1] - Y); y = Y + dy + s * (sc[:, 0] - X) + c * (sc[:, 1] - Y)
    xi = (x + 5.29) / 0.05 - 0.5; yi = (MH - 1) - ((y + 6.96) / 0.05 - 0.5)
    d = ndimage.map_coordinates(dt, [yi, xi], order=1, mode='nearest'); return np.mean(np.minimum(d, 0.3) ** 2)
def fit(rec):
    sc = rec['scan'].astype(float); X, Y, _ = rec['pose']; sc = sc[np.hypot(sc[:, 0] - X, sc[:, 1] - Y) < 4.0]
    best = None
    for dth0 in np.radians([-6, -3, 0, 3, 6]):
        r = optimize.minimize(cost, [0, 0, dth0], args=(sc, X, Y), method='Powell', options={'xtol': 1e-3, 'ftol': 1e-6})
        if best is None or r.fun < best.fun: best = r
    return cost([0, 0, 0], sc, X, Y) ** .5, best.fun ** .5, best.x
if __name__ == '__main__':
    for f, step in ((r'f2a6/f2a12_lviz.npz', 5), (r'f2a6/f2a12_g34.npz', 10), (r'f2a6/f2a10_gviz.npz', 10)):
        R = np.load(f, allow_pickle=True)['recs']; print('==', f)
        for r in R[::step]:
            e0, e1, (dx, dy, dth) = fit(r)
            print('  t%5.1f 자세 (%.2f, %.2f, %4.0f°) 잔차 %.3f → %.3f m | 필요 보정 dx %+.3f dy %+.3f dθ %+.1f°' % (r['t'], *r['pose'][:2], math.degrees(r['pose'][2]), e0, e1, dx, dy, math.degrees(dth)))
