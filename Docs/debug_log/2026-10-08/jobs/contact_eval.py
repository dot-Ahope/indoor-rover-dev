# 10-08 §3.5: f2e1 상자 ② 접촉 — 복귀 구간 0.5 s 마다 로컬 코스트맵(MPPI 가 보는 지도)의 상자 자리 치명·내접 칸, 차체 외곽 안 칸, 로버 자세·지령, MPPI 최적 궤적이 상자 칸과 겹치나
import numpy as np, math, time, sys
Z = np.load('fz_f2e1.npz'); tr, mo = Z['traj'], Z['mo']; XF, XB, HW = 0.262, -0.248, 0.165
K = lambda t: time.strftime('%H:%M:%S', time.localtime(t)) + ('.%d' % int((t % 1) * 10))
def at(X, t): i = min(max(np.searchsorted(X[:, 0], t), 0), len(X) - 1); return X[i, 1:4]
for k, t in enumerate(Z['lcm_t']):
    if not (K(t) >= '13:36:05' and K(t) <= '13:36:40'): continue
    g = Z['lcm'][k].astype(np.int16) & 0xFF; r, ox, oy = Z['lcm_meta'][k]; mx, my, mth = at(mo, t); c, s = math.cos(mth), math.sin(mth)
    iy, ix = np.nonzero((g >= 99) & (g <= 100)); wx, wy = ox + (ix + .5) * r, oy + (iy + .5) * r; X, Y = mx + c * wx - s * wy, my + s * wx + c * wy; v = g[iy, ix]
    box = (X > 0.95) & (X < 1.45) & (Y > -0.30) & (Y < 0.20)
    x, y, th = at(tr, t); cc, ss = math.cos(th), math.sin(th); bx = cc * (X - x) + ss * (Y - y); by = -ss * (X - x) + cc * (Y - y)
    inside = (bx > XB) & (bx < XF) & (np.abs(by) < HW)
    gap = np.hypot(np.where(bx > XF, bx - XF, np.where(bx < XB, XB - bx, 0)), np.maximum(np.abs(by) - HW, 0))
    lb = box & (v == 100)
    j = np.argmin(np.abs(Z['cmd'][:, 0] - t)); cv = Z['cmd'][j, 1:]
    print('%s 로버 (%.2f,%.2f,%+4.0f°) v %+.3f w %+.2f | 상자 자리 치명 %2d · 내접 %2d | 차체 안 치명 %d · 내접 %d | 상자 치명 칸까지 %s' % (
        K(t), x, y, math.degrees(th), cv[0], cv[1], lb.sum(), (box & (v == 99)).sum(), (inside & (v == 100)).sum(), (inside & (v == 99)).sum(), ('%.3f m' % gap[lb].min()) if lb.any() else '없음'))
