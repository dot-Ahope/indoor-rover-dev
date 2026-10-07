# 10-07 §3: G4 가 주행 중 곡선(전진하며 회전)에서 정상 전진 속도를 오염으로 보는가 — 회전 표본을 EKF B 전진 속도로 나눠 σ 키움·버림 비율
import numpy as np, math
LY = math.pi - 0.04677
for n in ('f2c1', 'f2c2'):
    Z = np.load('x913_%s.npz' % n); Bv, raw, gt = Z['Bv'], Z['raw'], Z['gated']
    w = np.interp(raw[:, 0], Bv[:, 0], Bv[:, 3]); v = np.interp(raw[:, 0], Bv[:, 0], Bv[:, 1])
    c, s = math.cos(LY), math.sin(LY); bvx = c * raw[:, 1] - s * raw[:, 2]; bvy = s * raw[:, 1] + c * raw[:, 2]; sp = np.hypot(bvx, bvy)
    # 게이트 출력은 같은 rf2o 메시지를 바로 다시 낸 것 — bag 수신 시각으로 가장 가까운 것(30 ms 안)을 짝지음(첫 판은 시각 반올림 일치로 짝지어 거의 다 '버림' 으로 잘못 셈)
    j = np.clip(np.searchsorted(gt[:, 0], raw[:, 0]), 1, len(gt) - 1); j = np.where(np.abs(gt[j - 1, 0] - raw[:, 0]) < np.abs(gt[j, 0] - raw[:, 0]), j - 1, j)
    passed = np.abs(gt[j, 0] - raw[:, 0]) < 0.03; cov = np.where(passed, gt[j, 3], np.nan)
    rot = np.abs(w) > 0.15
    for lab, sel in (('제자리(|v_B|<0.03)', rot & (np.abs(v) < 0.03)), ('곡선(|v_B|≥0.03)', rot & (np.abs(v) >= 0.03))):
        k = sel.sum(); rej = (sel & ~passed).sum(); soft = (sel & passed & (cov > 0.03 ** 2 * 1.5)).sum()
        print('%s %-18s 표본 %3d | rf2o |v| 중앙 %.3f m/s · EKF v 중앙 %.3f | σ 키움 %3d (%.0f %%) · 버림 %2d (%.0f %%)' % (n, lab, k, np.median(sp[sel]) if k else 0, np.median(np.abs(v[sel])) if k else 0, soft, 100 * soft / max(k, 1), rej, 100 * rej / max(k, 1)))
