# 10-07 §3.3: f2c2 W3 통로 구간 — 로컬 코스트맵 치명 칸이 통로를 좁혔나(정리 11:12:09 = 러너 t≈235 전후 비교), 라이다 근거 유무
import numpy as np, math
from scipy.spatial import cKDTree
Z = np.load('x912_f2c2.npz'); T0 = 1791338894.0; LX, LY = 0.152, math.pi - 0.04677; XB, XF, HW = -0.248, 0.262, 0.165
tr, mo = Z['traj'], Z['mo']
def m2(t): i = np.argmin(np.abs(mo[:, 0] - t)); return mo[i, 1:]
def pose(t): j = np.argmin(np.abs(tr[:, 0] - t)); return tr[j, 1:]
for k, t in enumerate(Z['lcm_t']):
    rt = t - T0
    if rt < 186 or rt > 262 or int(rt) % 4: continue
    g = Z['lcm'][k]; res, ox, oy = Z['lcm_meta'][k]; iy, ix = np.nonzero(g >= 100); wx, wy = ox + (ix + .5) * res, oy + (iy + .5) * res
    mx, my, mth = m2(t); c, s = math.cos(mth), math.sin(mth); X, Y = mx + c * wx - s * wy, my + s * wx + c * wy
    x, y, th = pose(t); c2, s2 = math.cos(th), math.sin(th); bx = c2 * (X - x) + s2 * (Y - y); by = -s2 * (X - x) + c2 * (Y - y)
    near = (np.abs(bx) < 1.0)   # 차체 앞뒤 1 m 안
    kk = np.argmin(np.abs(Z['scan_t'] - t)); r = Z['scan_r'][kk]; a0, da = Z['scan_a'][kk]; a = a0 + da * np.arange(len(r)) + LY; ok = np.isfinite(r) & (r > .05)
    sx, sy = LX + r[ok] * np.cos(a[ok]), r[ok] * np.sin(a[ok]); dd, _ = cKDTree(np.c_[sx, sy]).query(np.c_[bx[near], by[near]])
    L, Rr = by[near] > 0, by[near] < 0
    def side(m): 
        if not m.any(): return '   -   '
        return '%.3f' % (np.abs(by[near][m]).min() - HW)
    lid = np.abs(sy[(np.abs(sx) < 1.0)]) - HW
    print('t %3.0f | 앞뒤 1 m 안 치명 칸: 왼 %s · 오 %s m(외곽까지 옆 거리) | 라이다 옆 최소 왼 %.3f · 오 %.3f | 치명 중 라이다 7.5 cm 밖 %d/%d' % (
        rt, side(L), side(Rr), lid[sy[(np.abs(sx) < 1.0)] > 0].min(), lid[sy[(np.abs(sx) < 1.0)] < 0].min(), (dd > .075).sum(), near.sum()))
