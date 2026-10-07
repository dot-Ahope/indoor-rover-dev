# 10-07 §1: G4 켠 합성 가림 결과(occm_eval.py 와 같은 계산, 입력만 g4/)
import numpy as np, math, glob, os
TAPE = [44.8, 10.8, 43.3, 16.1, 43.5, 17.6]; CR = np.array([0.262, -0.165])
def srt(a): return a[np.argsort(a[:, 0])]
def at(A, t): i = min(max(np.searchsorted(A[:, 0], t) - 1, 0), len(A) - 1); return A[i, 1:4]
def corner_d(p, p0):
    c0, s0 = math.cos(p0[2]), math.sin(p0[2]); dx, dy = p[0] - p0[0], p[1] - p0[1]; x, y, th = c0 * dx + s0 * dy, -s0 * dx + c0 * dy, p[2] - p0[2]
    c, s = math.cos(th), math.sin(th); return math.hypot(x + c * CR[0] - s * CR[1] - CR[0], y + s * CR[0] + c * CR[1] - CR[1]) * 100
rows = {}
for f in sorted(glob.glob('g4/g4_*.npz')):
    Z = np.load(f); B, T = srt(Z['B']), srt(Z['T'])
    yaw = np.unwrap(T[:, 3]); t = T[:, 0]; w = np.gradient(yaw, t)
    # 정지 구간(|ω| < 0.02 가 2 s 이상) 끝 시각 목록
    still = np.abs(w) < 0.02; segs = []; i = 0
    while i < len(t):
        if still[i]:
            j = i
            while j + 1 < len(t) and still[j + 1]: j += 1
            if t[j] - t[i] > 2.0: segs.append((t[i], t[j]))
            i = j + 1
        else: i += 1
    # 회전 사이 정지 구간 7 개(시작 + 6 단계) — 회전량 85° 넘게 바뀐 경계만
    keep = [segs[0]]
    for s in segs[1:]:
        if abs(np.interp(s[1], t, yaw) - np.interp(keep[-1][1], t, yaw)) > math.radians(60): keep.append(s)
    keep = keep[:7]; t0 = keep[0][1] - 0.5
    eB = [corner_d(at(B, s[1] - 0.5), at(B, t0)) - TAPE[k] for k, s in enumerate(keep[1:])]
    eT = [corner_d(at(T, s[1] - 0.5), at(T, t0)) - TAPE[k] for k, s in enumerate(keep[1:])]
    c = os.path.basename(f)[3:-4]; rows[c] = (eB, eT)
    print('가림 %4s: 단계 %d | EKF B −줄자 %s | 평균 |오차| %.1f · 원위치(2·4·6) %s | (진실 대용 라이브 B 평균 %.1f)' % (c, len(eB), ' '.join('%+.1f' % e for e in eB), np.mean(np.abs(eB)), ' '.join('%+.1f' % eB[k] for k in (1, 3, 5) if k < len(eB)), np.mean(np.abs(eT))))
np.save('g4/g4_eval.npy', rows, allow_pickle=True)
# G4 판정 수(게이트 csv res 열) — 조건별 g4·g1·g2 와 회전 중 σ 키움(soft) 비율
import csv
for f in sorted(glob.glob('g4/g4_*_gate.csv')):
    R = list(csv.DictReader(open(f))); rot = [r for r in R if abs(float(r['w_gyro'])) > 0.15]
    cnt = {k: sum(r['res'] == k for r in R) for k in ('pass', 'g1', 'g2', 'g4')}
    soft = sum(1 for r in rot if r['res'] == 'pass' and 0.05 < math.hypot(float(r['bx']), float(r['by'])) <= 0.10)
    print('%-10s 판정 %s | 회전 중 표본 %d · σ 키움 %d · 버림 %d' % (os.path.basename(f)[3:-9], cnt, len(rot), soft, sum(r['res'] == 'g4' for r in rot)))
