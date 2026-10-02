# 10-02 §13 R1b: rf2o 속도의 좌표 보정 검증 — v_base = R(라이다 yaw)·v_rf2o − ω × r_lidar, 자이로(EKF) yaw 로 적분
#   후보: (a) 그대로 (b) R(π−0.04677) 회전만 (c) 회전 + 지렛대(라이다 x 0.152) 보정
import numpy as np, math, sys
LY, LX = math.pi - 0.04677, 0.152
def body(RF, mode):
    vx, vy, w = RF[:, 4], RF[:, 5], RF[:, 6]
    if mode == 'a': return vx, vy
    c, s = math.cos(LY), math.sin(LY); bx, by = c * vx - s * vy, s * vx + c * vy
    if mode == 'c': by = by - w * LX
    return bx, by
def integ(RF, OB, mode, ta, tb):
    bx, by = body(RF, mode); m = (RF[:, 0] >= ta) & (RF[:, 0] <= tb); t = RF[m, 0]
    yaw = np.interp(t, OB[:, 0], np.unwrap(OB[:, 3])); dt = np.diff(t, prepend=t[0])
    X = np.cumsum((np.cos(yaw) * bx[m] - np.sin(yaw) * by[m]) * dt); Y = np.cumsum((np.sin(yaw) * bx[m] + np.cos(yaw) * by[m]) * dt)
    y0 = yaw[0]; c, s = math.cos(y0), math.sin(y0); return c * X[-1] + s * Y[-1], -s * X[-1] + c * Y[-1], np.sum(np.hypot(np.diff(X), np.diff(Y)))
for f, truth in (('f2a6/rf2o_rot3.npz', (-0.275, -0.245)), ('f2a6/rf2o_rot2.npz', None)):
    Z = np.load(f); RF = Z['rf'][np.argsort(Z['rf'][:, 0])]; OB = Z['ob'][np.argsort(Z['ob'][:, 0])]
    for mode in 'abc':
        dx, dy, L = integ(RF, OB, mode, RF[0, 0] + .5, RF[-1, 0] - .5)
        print('%s %s: 시작 기준 이동 (%+.3f, %+.3f) 크기 %.3f, 경로 %.2f m%s' % (f[5:], mode, dx, dy, math.hypot(dx, dy), L, '' if truth is None else ' | 줄자 (%+.3f, %+.3f)' % truth))
Z = np.load('f2a6/rf2o_f2b4.npz'); RF = Z['rf'][np.argsort(Z['rf'][:, 0])]; OB = Z['ob'][np.argsort(Z['ob'][:, 0])]
te = OB[:, 0]; ye = np.unwrap(OB[:, 3]); vxe = np.full(len(RF), np.nan); we = np.full(len(RF), np.nan)
for k, t in enumerate(RF[:, 0]):
    i = np.searchsorted(te, t)
    if 2 <= i < len(te):
        a, b = OB[i - 2], OB[i]; dt = b[0] - a[0]; c, s = math.cos(a[3]), math.sin(a[3]); vxe[k] = (c * (b[1] - a[1]) + s * (b[2] - a[2])) / dt; we[k] = (ye[i] - ye[i - 2]) / dt
for mode in 'abc':
    bx, by = body(RF, mode); m = np.isfinite(vxe) & (abs(vxe) > 0.04) & (abs(we) < 0.05)
    r = (abs(we) > 0.25) & (abs(vxe) < 0.02)
    print('f2b4 %s: 직진(|ω|<0.05) vx 비 %.3f · vy 중앙 %+.4f (표본 %d) | 제자리 회전(|ω|>0.25) vy 중앙 %+.4f, |v| 중앙 %.4f (표본 %d)' % (mode, np.median(bx[m] / vxe[m]), np.median(by[m]), m.sum(), np.median(by[r]) if r.any() else np.nan, np.median(np.hypot(bx[r], by[r])) if r.any() else np.nan, r.sum()))
