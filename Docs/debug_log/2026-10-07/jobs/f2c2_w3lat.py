# 10-07 §5: W3 떨림 구간 — 계획 경로 대비 옆 벗어남·방향 차(4 s 마다), 쓰인 계획 시각
import numpy as np, math
Z = np.load('x912_f2c2.npz'); T0 = 1791338894.0; tr = Z['traj']; pt, pn, pxy = Z['plan_t'], Z['plan_n'], Z['plan_xy']; off = np.r_[0, np.cumsum(pn)]
for rt in range(184, 262, 4):
    t = T0 + rt; j = np.argmin(np.abs(tr[:, 0] - t)); x, y, th = tr[j, 1:]; k = np.flatnonzero(pt <= t)[-1]; Q = pxy[off[k]:off[k + 1]]
    q = np.argmin(np.hypot(Q[:, 0] - x, Q[:, 1] - y)); q2 = min(q + 3, len(Q) - 1); tg = math.atan2(Q[q2, 1] - Q[q, 1], Q[q2, 0] - Q[q, 0])
    lat = -math.sin(tg) * (x - Q[q, 0]) + math.cos(tg) * (y - Q[q, 1]); da = (th - tg + math.pi) % (2 * math.pi) - math.pi
    print('t %3d 자세 (%.2f,%.2f,%+4.0f°) | 계획 t %3.0f | 옆 %+.3f m · 방향 %+4.0f° | 계획 끝까지 %.2f m' % (rt, x, y, math.degrees(th), pt[k] - T0, lat, math.degrees(da), np.hypot(*(Q[-1] - [x, y]))))
