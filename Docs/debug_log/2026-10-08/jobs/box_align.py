# 10-08 §3.7: 복귀 구간 상자 ② — 로컬(MPPI)·전역(계획기) 지도의 상자 칸 위치 비교, 경로 ↔ 상자, 차체 ↔ 상자. 인자: npz 시작HH:MM:SS 끝HH:MM:SS
import numpy as np, math, time, sys
Z = np.load(sys.argv[1]); tr, mo = Z['traj'], Z['mo']; XF, XB, HW = 0.262, -0.248, 0.165
K = lambda t: time.strftime('%H:%M:%S', time.localtime(t))
pt, pn, pxy = Z['plan_t'], Z['plan_n'], Z['plan_xy']; off = np.r_[0, np.cumsum(pn)]
def at(X, t): i = min(max(np.searchsorted(X[:, 0], t), 0), len(X) - 1); return X[i, 1:4]
def cells(G, meta, t, frame_odom, vmin):
    g = G.astype(np.int16) & 0xFF; r, ox, oy = meta; iy, ix = np.nonzero((g >= vmin) & (g <= 100)); wx, wy = ox + (ix + .5) * r, oy + (iy + .5) * r
    if frame_odom: mx, my, mth = at(mo, t); c, s = math.cos(mth), math.sin(mth); wx, wy = mx + c * wx - s * wy, my + s * wx + c * wy
    sel = (wx > 0.95) & (wx < 1.45) & (wy > -0.15) & (wy < 0.25); return np.c_[wx[sel], wy[sel]]   # 상자 ② 자리(상자 ① 은 y < −0.25 라 뺌)
for t in np.arange(*[time.mktime(time.strptime(time.strftime('%Y-%m-%d ', time.localtime(tr[0, 0])) + a, '%Y-%m-%d %H:%M:%S')) for a in sys.argv[2:4]], 2.0):
    li = np.searchsorted(Z['lcm_t'], t) - 1; gi = np.searchsorted(Z['gcm_t'], t) - 1
    L = cells(Z['lcm'][li], Z['lcm_meta'][li], Z['lcm_t'][li], True, 100); G = cells(Z['gcm'][gi], Z['gcm_meta'][gi], Z['gcm_t'][gi], False, 100)
    x, y, th = at(tr, t); c, s = math.cos(th), math.sin(th)
    def gap(P):
        if not len(P): return float('nan')
        bx = c * (P[:, 0] - x) + s * (P[:, 1] - y); by = -s * (P[:, 0] - x) + c * (P[:, 1] - y)
        return np.hypot(np.where(bx > XF, bx - XF, np.where(bx < XB, XB - bx, 0)), np.maximum(np.abs(by) - HW, 0)).min()
    i = np.searchsorted(pt, t) - 1; P = pxy[off[i]:off[i + 1]]; j = np.argmin(np.hypot(P[:, 0] - x, P[:, 1] - y)); Pa = P[j:]
    pl = np.hypot(Pa[:, None, 0] - L[None, :, 0], Pa[:, None, 1] - L[None, :, 1]).min() if len(L) else float('nan')
    print('%s 로버 (%.2f,%.2f) | 상자 ② 치명 칸: 로컬 %2d %s · 전역 %2d %s | 경로↔로컬 상자 %.2f m | 차체↔로컬 상자 %.2f m' % (K(t), x, y, len(L),
        ('중심(%.2f,%.2f)' % tuple(L.mean(0))) if len(L) else '            ', len(G), ('중심(%.2f,%.2f)' % tuple(G.mean(0))) if len(G) else '', pl, gap(L)))
