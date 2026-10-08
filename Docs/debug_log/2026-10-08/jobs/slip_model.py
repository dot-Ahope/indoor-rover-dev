# 10-08 §5.11: 회전 중 '뒤로 밀림' 보정 모델 오프라인 적합(실행 1·2 40 회, 한 개 빼고 검증 LOO)
#   E = 실제 이동 − 휠 추측항법(시작 차체 기준 앞, 옆). 모델은 앞뒤 성분만 보정(옆은 0 유지).
#   M1: ex = −k·|Δθ|            (회전량 비례)
#   M2: ex = −k·|Δθ| + c·wx      (회전량 + 휠 전진 거리 비례 — 앞 회전 0.30·뒤 1.66 반영)
import csv, numpy as np
R = [dict((k, float(v)) for k, v in o.items()) for f in ('ratio_bag_rt1.csv', 'ratio_bag_rt2.csv') for o in csv.DictReader(open(f))]
th = np.radians(np.abs([o['rot'] for o in R])); wx = np.array([o['wx'] for o in R]); ex = np.array([o['ex'] for o in R]); ey = np.array([o['ey'] for o in R])
X = {'M1': np.c_[-th], 'M2': np.c_[-th, wx]}
def err(pred): return np.hypot(ex - pred, ey) * 100 * 90 / np.degrees(th)   # 90°당 남는 오차 cm
print('M0 보정 없음: 90°당 오차 중앙 %.1f · 평균 %.1f cm' % (np.median(err(0 * ex)), err(0 * ex).mean()))
for nm, A in X.items():
    p = np.zeros(len(R))
    for i in range(len(R)):
        m = np.arange(len(R)) != i; coef, *_ = np.linalg.lstsq(A[m], ex[m], rcond=None); p[i] = A[i] @ coef
    coef, *_ = np.linalg.lstsq(A, ex, rcond=None); e = err(p)
    print('%s 계수 %s → LOO 90°당 오차 중앙 %.1f · 평균 %.1f cm (최대 %.1f)' % (nm, np.round(coef, 3), np.median(e), e.mean(), e.max()))
