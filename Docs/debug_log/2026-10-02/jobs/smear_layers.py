# 10-02 §10: 회전 중 번짐 층 분리 — 서쪽 구조물(y −5.95~−5.35, x −2.1~−1.6)의 안쪽 면(가장 큰 x)을 층별로
#   라이다(map·odom), nvblox 장애 칸(≤ 0.05 m, map 으로 옮김), 로컬 치명 칸(map 으로 옮김), 그리고 로컬 치명 중 nvblox 장애 0.1 m 안에 없는 것(= 라이다 obstacle 층 몫 추정)
import sys, numpy as np, math
L = np.load(sys.argv[1], allow_pickle=True)['recs']; T0 = float(sys.argv[2]) if len(sys.argv) > 2 else 0
REG = lambda x, y: (y > -5.95) & (y < -5.35) & (x < -1.6) & (x > -2.1)
print('  t   로버θ  map→odom x | 라이다 map/odom | nvblox(map) | 로컬치명(map) | 로컬치명 중 nvblox 없음(map)')
for r in L:
    if 'nv' not in r or 'scan' not in r: continue
    X, Y, T = r['pose']; tx, ty, tw = r['mo']; c, s = math.cos(tw), math.sin(tw)
    to_map = lambda x, y: (tx + c * x - s * y, ty + s * x + c * y)
    sc = r['scan'].astype(float); m = REG(sc[:, 0], sc[:, 1]); wm = np.percentile(sc[m, 0], 95) if m.sum() > 3 else np.nan
    wo = np.percentile(c * (sc[m, 0] - tx) + s * (sc[m, 1] - ty), 95) if m.sum() > 3 else np.nan
    nv = r['nv']; nox, noy, nres, unk = r['nv_o']; ii, jj = np.where((nv <= 0.05) & (nv < unk * .5))
    vx, vy = to_map(nox + (jj + .5) * nres, noy + (ii + .5) * nres); k = REG(vx, vy); nvm = vx[k].max() if k.any() else np.nan
    g = r['gcm']; ox, oy, res = r['gcm_o']; ii, jj = np.where(g >= 100); lx, ly = to_map(ox + (jj + .5) * res, oy + (ii + .5) * res); kl = REG(lx, ly)
    lm = lx[kl].max() if kl.any() else np.nan
    if kl.any() and k.any():
        d = np.min(np.hypot(lx[kl][:, None] - vx[k][None, :], ly[kl][:, None] - vy[k][None, :]), axis=1); lo = lx[kl][d > 0.1]
        lom = lo.max() if len(lo) else np.nan
    else: lom = np.nan
    print('%4.0f %5.0f° %+.3f | %.3f / %.3f | %.3f | %.3f | %.3f' % (r['t'] - T0, math.degrees(T), tx, wm, wo, nvm, lm, lom))
