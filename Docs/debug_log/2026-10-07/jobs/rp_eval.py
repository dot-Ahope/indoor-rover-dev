# 10-07 §4 B: f2c2 재생 abs vs wheel — 게이트 csv 로 회전 표본(제자리·곡선)의 G4 σ 키움·버림 비율, 재생 EKF B 와 라이브 B 궤적 차
import numpy as np, csv, math, sys
def yawd(a): return (a + math.pi) % (2 * math.pi) - math.pi
for ref in ('abs', 'wheel'):
    R = list(csv.DictReader(open('rp/rp_f2c2_%s_gate.csv' % ref)))
    w = np.array([float(r['w_gyro']) for r in R]); vw = np.array([float(r['v_wheel']) for r in R]); bx = np.array([float(r['bx']) for r in R]); by = np.array([float(r['by']) for r in R])
    res = np.array([r['res'] for r in R]); vb = np.hypot(bx - vw, by) if ref == 'wheel' else np.hypot(bx, by)
    rot = np.abs(w) > 0.15
    for lab, sel in (('제자리(|v_휠|<0.03)', rot & (np.abs(vw) < 0.03)), ('곡선(|v_휠|≥0.03)', rot & (np.abs(vw) >= 0.03))):
        k = sel.sum(); soft = (sel & (res == 'pass') & (vb > 0.05)).sum(); rej = (sel & (res == 'g4')).sum()
        print('%-5s %-18s 표본 %3d | 판정량 중앙 %.3f · 90 %% %.3f m/s | σ 키움 %3d (%.0f %%) · 버림 %2d (%.0f %%) | 합 %.0f %%' % (ref, lab, k, np.median(vb[sel]), np.percentile(vb[sel], 90), soft, 100 * soft / k, rej, 100 * rej / k, 100 * (soft + rej) / k))
    print('%-5s 전체 판정 %s' % (ref, {x: int((res == x).sum()) for x in ('pass', 'g1', 'g2', 'g4')}))
    Z = np.load('rp/rp_f2c2_%s.npz' % ref); B, T = Z['B'][np.argsort(Z['B'][:, 0])], Z['T'][np.argsort(Z['T'][:, 0])]
    # 재생 EKF 는 bag 시작에서 원점, 라이브 B 는 그때 이미 odom (−1.2, −5.5) — 시작 자세에 맞춰 이동량끼리 비교(첫 판은 원점 그대로 비교해 5.6 m 로 나옴)
    t0 = max(B[0, 0], T[0, 0]) + 1.0; b0 = B[np.searchsorted(B[:, 0], t0)]; s0 = T[np.searchsorted(T[:, 0], t0)]; s = T[:, 0] >= t0
    def rel(P, p0): c, sn = math.cos(p0[3]), math.sin(p0[3]); dx, dy = P[:, 1] - p0[1], P[:, 2] - p0[2]; return c * dx + sn * dy, -sn * dx + c * dy
    Bx, By = rel(B, b0); Tx, Ty = rel(T[s], s0); bx_ = np.interp(T[s, 0], B[:, 0], Bx); by_ = np.interp(T[s, 0], B[:, 0], By); T = np.c_[T[s, 0], Tx, Ty]
    d = np.hypot(bx_ - T[:, 1], by_ - T[:, 2]); print('%-5s 재생 B − 라이브 B 위치 차: 끝 %.1f · 최대 %.1f · 중앙 %.1f cm (같은 bag — 진실 아님)' % (ref, 100 * d[-1], 100 * d.max(), 100 * np.median(d)))
