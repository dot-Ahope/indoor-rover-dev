# 10-07 §8: 상자 ②(map x 1.1~1.3, y −0.1~+0.1) 가 전역 코스트맵에 언제 있고 언제 사라지나 — 로버 거리·카메라 화각 안 여부와 함께
import numpy as np, math
for f, T0, g6, lab in (('x912_f2c2.npz', 1791338894.0, 307.8, 'f2c2'), ('x921_f2d2.npz', 1791346297.0, 303.5, 'f2d2')):
    Z = np.load(f); tr = Z['traj']; print('====', lab, '(목표 10 시작 뒤 s)')
    for k, t in enumerate(Z['gcm_t']):
        rt = t - T0 - g6
        if rt < 30 or int(rt) % 4: continue
        g = Z['gcm'][k]; res, ox, oy = Z['gcm_meta'][k]
        ix0, ix1 = int((1.1 - ox) / res), int((1.3 - ox) / res); iy0, iy1 = int((-0.1 - oy) / res), int((0.1 - oy) / res)
        box = g[iy0:iy1 + 1, ix0:ix1 + 1]; n100 = int((box >= 100).sum())
        j = np.argmin(np.abs(tr[:, 0] - t)); x, y, th = tr[j, 1:]; dx, dy = 1.2 - x, 0.0 - y; d = math.hypot(dx, dy)
        bear = math.degrees((math.atan2(dy, dx) - th + math.pi) % (2 * math.pi) - math.pi)
        # D455 수평 화각 ≈ ±43°, 카메라 앞 0.45 m 근거리 컷(depth_relay), 전역 카메라 표시 거리 ≤ 1.2 m
        cam = abs(bear) < 43 and 0.45 < d - 0.26 < 1.2
        print('  %+6.1f s 상자② 치명 칸 %2d | 로버 (%.2f,%.2f,%+4.0f°) 상자까지 %.2f m · 방위 %+4.0f° | 카메라 표시 조건 %s' % (rt, n100, x, y, math.degrees(th), d, bear, '예' if cam else '아니오'))
