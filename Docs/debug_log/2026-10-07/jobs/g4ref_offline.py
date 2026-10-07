# 10-07 §4 A(오프라인): 10-06 보정 재생 csv(합성 5 조건, bag_step1 = 제자리 회전 시험)에서 G4 판정량 abs vs wheel — 판정(통과·σ 배수·버림)이 바뀌는 회전 표본 수
import numpy as np, csv
def fac(v): return np.where(v > 0.10, np.inf, np.where(v > 0.05, 1 + 9 * np.minimum(1, (v - 0.05) / 0.05), 1.0))
for c in ('clean', 'static50', 'A_walk08', 'C_sway', 'E_fast'):
    R = list(csv.DictReader(open('qcal/qcal_%s_gate.csv' % c)))
    w = np.array([float(r['w_gyro']) for r in R]); vw = np.array([float(r['v_wheel']) for r in R]); bx = np.array([float(r['bx']) for r in R]); by = np.array([float(r['by']) for r in R])
    rot = np.abs(w) > 0.15; a = fac(np.hypot(bx, by))[rot]; b = fac(np.hypot(bx - vw, by))[rot]
    ch = ~((a == b) | (np.isfinite(a) & np.isfinite(b) & (np.abs(a - b) < 0.5)))
    print('%-9s 회전 표본 %3d | 휠 |vx| 중앙 %.4f · 최대 %.3f m/s | 판정 바뀜 %d (버림↔통과 %d, σ 배수 0.5 넘게 %d)' % (c, rot.sum(), np.median(np.abs(vw[rot])), np.abs(vw[rot]).max(), ch.sum(), (np.isfinite(a) != np.isfinite(b)).sum(), (ch & np.isfinite(a) & np.isfinite(b)).sum()))
