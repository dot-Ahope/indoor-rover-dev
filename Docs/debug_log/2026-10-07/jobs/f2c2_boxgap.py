# 10-07 §2.5: 상자(카메라만 본 치명 칸 묶음, map x 1.25~1.75 · y −0.55~−0.2) ↔ 차체 외곽 거리, 그리고 계획 경로 대비 옆 벗어남·방향 차(1 s 마다)
import numpy as np, math
Z = np.load('x912_f2c2.npz'); T0 = 1791338894.0; G6 = T0 + 307.8; XB, XF, HW = -0.248, 0.262, 0.165
tr, mo = Z['traj'], Z['mo']; pt, pn, pxy = Z['plan_t'], Z['plan_n'], Z['plan_xy']; off = np.r_[0, np.cumsum(pn)]
def m2(t): i = np.argmin(np.abs(mo[:, 0] - t)); return mo[i, 1:]
for k, t in enumerate(Z['lcm_t']):
    if t < G6 + 78 or t > G6 + 112 or round(t - G6) % 2: continue
    g = Z['lcm'][k]; res, ox, oy = Z['lcm_meta'][k]; iy, ix = np.nonzero(g >= 100); wx, wy = ox + (ix + .5) * res, oy + (iy + .5) * res
    mx, my, mth = m2(t); c, s = math.cos(mth), math.sin(mth); X, Y = mx + c * wx - s * wy, my + s * wx + c * wy
    box = (X > 1.2) & (X < 1.8) & (Y > -0.6) & (Y < -0.15)
    j = np.argmin(np.abs(tr[:, 0] - t)); x, y, th = tr[j, 1:]; c, s = math.cos(th), math.sin(th)
    bx = c * (X[box] - x) + s * (Y[box] - y); by = -s * (X[box] - x) + c * (Y[box] - y)
    d = np.hypot(np.where(bx > XF, bx - XF, np.where(bx < XB, XB - bx, 0)), np.maximum(np.abs(by) - HW, 0))
    kk = np.flatnonzero(pt <= t)[-1]; Q = pxy[off[kk]:off[kk + 1]]; q = np.argmin(np.hypot(Q[:, 0] - x, Q[:, 1] - y)); q2 = min(q + 3, len(Q) - 1)
    tang = math.atan2(Q[q2, 1] - Q[q, 1], Q[q2, 0] - Q[q, 0]); lat = -math.sin(tang) * (x - Q[q, 0]) + math.cos(tang) * (y - Q[q, 1])
    dang = (th - tang + math.pi) % (2 * math.pi) - math.pi
    print('%+6.1f s 자세 (%.2f,%.2f,%+4.0f°) | 상자 칸 %3d, 외곽까지 최소 %s | 계획(%+.0f s) 대비 옆 %+.3f m(+ = 왼쪽), 방향 %+4.0f°(+ = 왼쪽으로 더 틂)' % (
        t - G6, x, y, math.degrees(th), box.sum(), ('%.3f m' % d.min()) if box.any() else '-', pt[kk] - G6, lat, math.degrees(dang)))
