# 10-02 §13 R1: rf2o 재생 결과 vs SLAM(map 자세) vs EKF(odom 자세) — 회전 시험 동안 위치 변화·회전 추적
import sys, os, numpy as np, math
for f in sys.argv[1:]:
    Z = np.load(f); RF, MO, OB = Z['rf'], Z['mo'], Z['ob']
    RF = RF[np.argsort(RF[:, 0])]; MO = MO[np.argsort(MO[:, 0])]; OB = OB[np.argsort(OB[:, 0])]
    def at(A, t): i = max(np.searchsorted(A[:, 0], t) - 1, 0); return A[i, 1:4]
    def mapP(t):
        mx, my, mt = at(MO, t); ox, oy, ot = at(OB, t); c, s = math.cos(mt), math.sin(mt); return np.array([mx + c * ox - s * oy, my + s * ox + c * oy, mt + ot])
    t0, t1 = RF[0, 0], RF[-1, 0]
    # 회전 시작 전 자세 기준으로 끝까지, 그리고 매 정지 구간(각 회 끝)
    def summary(ta, tb):
        r0, r1 = RF[np.argmin(abs(RF[:, 0] - ta)), 1:4], RF[np.argmin(abs(RF[:, 0] - tb)), 1:4]
        m0, m1 = mapP(ta), mapP(tb); e0, e1 = at(OB, ta), at(OB, tb)
        return (math.hypot(*(r1[:2] - r0[:2])), math.hypot(*(m1[:2] - m0[:2])), math.hypot(*(e1[:2] - e0[:2])),
                math.degrees(r1[2] - r0[2]), math.degrees(((m1[2] - m0[2]) + math.pi) % (2 * math.pi) - math.pi), math.degrees(((e1[2] - e0[2]) + math.pi) % (2 * math.pi) - math.pi))
    a = summary(t0 + 0.5, t1 - 0.5)
    print('%s: 시험 전체 순 이동 rf2o %.3f · SLAM %.3f · EKF %.3f m | 순 회전 rf2o %+.1f · SLAM %+.1f · EKF %+.1f°' % ((os.path.basename(f),) + a))
    # 회전 속도 비교: rf2o ω vs EKF ω(odom 자세 미분)
    w_rf = RF[:, 6]; te = OB[:, 0]; ye = np.unwrap(OB[:, 3]); w_e = np.interp(RF[:, 0], te[1:], np.diff(ye) / np.maximum(np.diff(te), 1e-3))
    mv = abs(w_e) > 0.2
    print('   회전 중 ω 비 rf2o/EKF 중앙 %.3f (표본 %d) | rf2o 병진 속도 |v| 회전 중 중앙 %.3f · 최대 %.3f m/s' % (np.median(w_rf[mv] / w_e[mv]), mv.sum(), np.median(np.hypot(RF[mv, 4], RF[mv, 5])), np.hypot(RF[mv, 4], RF[mv, 5]).max()))
    # 회별 누적 경로(이동 길이) 비교
    seg = lambda A: np.sum(np.hypot(np.diff(A[:, 1]), np.diff(A[:, 2])))
    MP = np.array([mapP(t) for t in RF[:, 0]])
    print('   이동 경로 길이 rf2o %.3f · SLAM %.3f · EKF %.3f m' % (seg(RF), np.sum(np.hypot(np.diff(MP[:, 0]), np.diff(MP[:, 1]))), seg(OB)))
