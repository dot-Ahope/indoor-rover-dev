# 10-07 §3.3: W3 통로 — 진행 방향 앞 띠(차체 폭 ±0.27 m, 앞 0~1.2 m)의 치명·고비용 칸: 정리(t≈235) 전후, 라이다 근거 유무
import numpy as np, math
from scipy.spatial import cKDTree
Z = np.load('x912_f2c2.npz'); T0 = 1791338894.0; LX, LY = 0.152, math.pi - 0.04677; XF, HW = 0.262, 0.165
tr, mo = Z['traj'], Z['mo']
def m2(t): i = np.argmin(np.abs(mo[:, 0] - t)); return mo[i, 1:]
def pose(t): j = np.argmin(np.abs(tr[:, 0] - t)); return tr[j, 1:]
for k, t in enumerate(Z['lcm_t']):
    rt = t - T0
    if rt < 186 or rt > 250 or int(rt) % 3: continue
    g = Z['lcm'][k]; res, ox, oy = Z['lcm_meta'][k]
    for thr, lab in ((100, '치명'), (60, '비용≥60')):
        iy, ix = np.nonzero(g >= thr); wx, wy = ox + (ix + .5) * res, oy + (iy + .5) * res
        mx, my, mth = m2(t); c, s = math.cos(mth), math.sin(mth); X, Y = mx + c * wx - s * wy, my + s * wx + c * wy
        x, y, th = pose(t); c2, s2 = math.cos(th), math.sin(th); bx = c2 * (X - x) + s2 * (Y - y); by = -s2 * (X - x) + c2 * (Y - y)
        m = (bx > XF) & (bx < 1.2) & (np.abs(by) < HW + 0.10)
        if lab == '치명':
            kk = np.argmin(np.abs(Z['scan_t'] - t)); r = Z['scan_r'][kk]; a0, da = Z['scan_a'][kk]; a = a0 + da * np.arange(len(r)) + LY; ok = np.isfinite(r) & (r > .05)
            dd, _ = cKDTree(np.c_[LX + r[ok] * np.cos(a[ok]), r[ok] * np.sin(a[ok])]).query(np.c_[bx[m], by[m]]) if m.any() else (np.zeros(0), 0)
            out = '앞 띠 치명 %3d (최근 %s, 카메라만 %d)' % (m.sum(), ('%.2f m' % (bx[m].min() - XF)) if m.any() else '  -   ', (dd > .075).sum())
        else: out += ' | 비용≥60 %3d (최근 %s)' % (m.sum(), ('%.2f m' % (bx[m].min() - XF)) if m.any() else '  -   ')
    print('t %3.0f %s' % (rt, out))
