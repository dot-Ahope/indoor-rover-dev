#!/usr/bin/env python3
"""09-29 §3 판정: L1·L2 회전별 EKF(B2·B3 켬)·SLAM 이동 vs 스캔 직접 정합(정답). 값은 j636(러너 출력)·j637(스캔 정합) 원문에서 옮김(cm)."""
import math, statistics as st
# (이름, 회전각°, 정답 d, EKF, SLAM, 완전 회전 여부)
R = [('L1-1', -178.1, (-4.9, 7.6), (-5.8, 10.3), (-4.3, 8.5), 1),
     ('L1-2', -178.4, (-2.2, 9.9), (-5.8, 10.2), (-0.9, 9.5), 1),
     ('L1-3', -177.6, (-9.0, 14.5), (-6.0, 10.2), (-10.0, 13.2), 1),
     ('L2-1', 175.4, (-9.7, -13.9), (-6.7, -18.9), (-10.8, -13.2), 1),
     ('L2-2', 93.0, (-10.6, 3.1), (-12.5, -6.9), (-8.6, 6.0), 0)]
e = lambda a, b: math.hypot(a[0] - b[0], a[1] - b[1])
print('회전   정답(cm)        |정답|  EKF 오차  SLAM 오차')
for n, th, d, k, s, f in R:
    print('%-5s (%+5.1f,%+5.1f)  %5.1f   %5.1f     %5.1f%s' % (n, *d, math.hypot(*d), e(k, d), e(s, d), '' if f else '  (부분 93°, 안전 정지)'))
F = [r for r in R if r[5]]
ek = [e(r[3], r[2]) for r in F]; sl = [e(r[4], r[2]) for r in F]; mg = [math.hypot(*r[2]) for r in F]
print('완전 회전 n=%d: EKF 오차 중앙값 %.1f cm (최대 %.1f), |정답| 중앙값 %.1f → 비 %.0f %%, ≤7 cm %d/%d' % (len(F), st.median(ek), max(ek), st.median(mg), 100 * st.median(ek) / st.median(mg), sum(x <= 7 for x in ek), len(F)))
print('            SLAM 오차 중앙값 %.1f cm (최대 %.1f)' % (st.median(sl), max(sl)))
# L-c: 반시계 0.38 회전축 p = (I − R(θ))⁻¹ d
def pivot(th, d):
    t = math.radians(th); a, b = 1 - math.cos(t), math.sin(t)   # I−R = [[a, b], [−b, a]]
    det = a * a + b * b
    return ((a * d[0] - b * d[1]) / det, (b * d[0] + a * d[1]) / det)
p = pivot(175.4, (-9.7, -13.9)); print('L2-1 반시계 0.38 회전축 p = (%+.1f, %+.1f) cm (현 반시계 공용 (−2.9, −9.5), 09-28 S2 (+2.4, −7.6))' % p)
for n, th, d, k, s, f in F[:3]:
    print('  참고 %s 시계 p = (%+.1f, %+.1f) cm (현 시계 공용 (−2.9, +5.2))' % ((n,) + pivot(th, d)))
