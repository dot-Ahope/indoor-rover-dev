# 10-07 §3: f2c1·f2c2 — ③-b 회전 구간 번짐(EKF B·그림자 A 대 SLAM), ③-c 게이트 비용, rf2o 발행률, map→odom 보정이 어디서 쌓였나
import numpy as np, math
def ang(a): return (a + math.pi) % (2 * math.pi) - math.pi
def at(X, t): i = min(max(np.searchsorted(X[:, 0], t) - 1, 0), len(X) - 1); return X[i, 1:4]
def comp(m, o): c, s = math.cos(m[2]), math.sin(m[2]); return np.array([m[0] + c * o[0] - s * o[1], m[1] + s * o[0] + c * o[1], m[2] + o[2]])
for n in ('f2c1', 'f2c2'):
    Z = np.load('x913_%s.npz' % n); mo, ob, A, Bv, raw, gt = Z['mo'], Z['ob'], Z['A'], Z['Bv'], Z['raw'], Z['gated']
    T = Bv[-1, 0] - Bv[0, 0]; print('==== %s  길이 %.0f s · rf2o 원 %.2f Hz · 게이트 출력 %.2f Hz' % (n, T, len(raw) / T, len(gt) / T))
    w = np.interp(raw[:, 0], Bv[:, 0], Bv[:, 3]); rot_r = np.abs(w) > 0.15
    wg = np.interp(gt[:, 0], Bv[:, 0], Bv[:, 3]); rot_g = np.abs(wg) > 0.15; soft = rot_g & (gt[:, 3] > 0.03 ** 2 * 1.5)
    print('  ③-c 회전 중 rf2o 원 %d → 게이트 통과 %d (버림 %d = %.1f %%), 통과 중 σ 키움 %d · 직진·정지 버림 %d / %d' % (
        rot_r.sum(), rot_g.sum(), rot_r.sum() - rot_g.sum(), 100 * (rot_r.sum() - rot_g.sum()) / max(rot_r.sum(), 1), soft.sum(), (~rot_r).sum() - (~rot_g).sum(), (~rot_r).sum()))
    # 제자리 회전 구간: |ω| > 0.15 · |v| < 0.03 이 1.5 s 이상
    t = Bv[:, 0]; ip = (np.abs(Bv[:, 3]) > 0.15) & (np.abs(Bv[:, 1]) < 0.03)
    e = np.flatnonzero(np.diff(np.r_[0, ip.astype(int), 0])); segs = [(t[a], t[b - 1]) for a, b in zip(e[::2], e[1::2]) if t[b - 1] - t[a] > 1.5]
    rowsB, rowsA = [], []
    print('  ③-b 제자리 회전 구간(시작 기준 s, 회전량) | 진짜 이동(SLAM) | EKF B − SLAM | 그림자 A − SLAM  (cm)')
    for ts, te in segs:
        S0 = comp(at(mo, ts), at(ob, ts)); S1 = comp(at(mo, te + 2.0), at(ob, te))
        B0, B1 = at(ob, ts), at(ob, te); A0, A1 = at(A, ts), at(A, te); m = at(mo, ts)
        c, s = math.cos(m[2]), math.sin(m[2]); R = lambda d: np.array([c * d[0] - s * d[1], s * d[0] + c * d[1]])
        dS = S1[:2] - S0[:2]; dB = R(B1[:2] - B0[:2]); dA = R(A1[:2] - A0[:2])
        eB, eA = 100 * np.linalg.norm(dB - dS), 100 * np.linalg.norm(dA - dS); rowsB.append(eB); rowsA.append(eA)
        print('   %6.1f~%6.1f s %+5.0f° | %5.1f | %5.1f | %5.1f' % (ts - t[0], te - t[0], math.degrees(ang(B1[2] - B0[2])) if abs(B1[2]-B0[2]) < 6 else math.degrees(B1[2]-B0[2]), 100 * np.linalg.norm(dS), eB, eA))
    if rowsB: print('  → 회전 %d 구간: B − SLAM 평균 %.1f · 최대 %.1f cm | A − SLAM 평균 %.1f · 최대 %.1f cm | B < A 인 구간 %d/%d' % (len(rowsB), np.mean(rowsB), max(rowsB), np.mean(rowsA), max(rowsA), sum(b < a for b, a in zip(rowsB, rowsA)), len(rowsB)))
    # map→odom 보정이 회전 중에 쌓였나 직진 중에 쌓였나(보정 변화의 크기 합)
    dm = np.hypot(np.diff(mo[:, 1]), np.diff(mo[:, 2])); dy = np.abs(ang(np.diff(mo[:, 3]))); tm = mo[1:, 0]
    wr = np.abs(np.interp(tm, t, Bv[:, 3])) > 0.15
    print('  map→odom 변화 합: 위치 회전 중 %.3f · 그 밖 %.3f m | yaw 회전 중 %.2f · 그 밖 %.2f °  (끝 − 처음: Δ(%.3f, %.3f) m, %.2f°)' % (
        dm[wr].sum(), dm[~wr].sum(), math.degrees(dy[wr].sum()), math.degrees(dy[~wr].sum()), mo[-1, 1] - mo[0, 1], mo[-1, 2] - mo[0, 2], math.degrees(ang(mo[-1, 3] - mo[0, 3]))))
    big = np.flatnonzero(dm > 0.05); print('  한 번에 5 cm 넘는 보정 %d 회: %s' % (len(big), ' '.join('%.0fs/%.1fcm' % (tm[i] - t[0], 100 * dm[i]) for i in big[:12])))
