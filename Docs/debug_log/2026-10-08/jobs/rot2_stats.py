# 10-08 §4: rot2.py 결과(≥45° 회전)를 회전 종류별로 묶음. 종류는 트랙 속도로 정함(회전축 추정과 독립):
#   제자리 = 두 트랙이 반대 방향이고 둘 다 |v| ≥ 0.035 · 피벗 = 느린 트랙 |v| ≤ 0.02 · 나머지 = 중간
import glob, math, numpy as np
R = []
for f in sorted(glob.glob('rot2_f2*_*.npz')):
    d = np.load(f); b, s = f.split('_')[1], int(f.split('_')[2][:-4]); X, T = d['X'], d['T']; dth = math.degrees(X[-1, 2])
    if abs(dth) < 45: continue
    vl, vr = d['vl'], d['vr']; vw = (vl + vr) / 2; D = np.zeros(2)
    for k in range(len(T) - 1):
        h = (X[k, 2] + X[k + 1, 2]) / 2; D += vw[k] * (T[k + 1] - T[k]) * np.array([math.cos(h), math.sin(h)])
    E = X[-1, :2] - D; L, Rr = vl.mean(), vr.mean(); lo = min(abs(L), abs(Rr))
    kind = 'spin' if (L * Rr < 0 and lo >= 0.035) else ('pivot' if lo <= 0.02 else 'mid')
    back = (Rr < 0 if abs(Rr) > abs(L) else L < 0)   # 빠른 트랙이 뒤로 구름
    icr = d['icr']; ix, iy = np.nanmedian(icr[:, 0]), np.nanmedian(icr[:, 1])
    R.append((b, s, kind, dth, L, Rr, ix, iy, math.hypot(*E), math.hypot(*E) * 90 / abs(dth), back))
excl = {('f2e1', 238)}   # f2e1 복귀 상자 접촉 구간(§3.5) — 접촉 힘이 섞여 제외
print('bag   s    종류   회전°  L      R      | 축 앞 왼 cm | 미끄러짐 cm | 90°당 | 빠른 트랙 후진')
for r in sorted(R, key=lambda r: (r[2], r[9])):
    print('%-5s %4d %-5s %+5.0f %+.3f %+.3f | %+5.1f %+5.1f | %5.1f | %5.1f | %s%s' % (r[0], r[1], r[2], r[3], r[4], r[5], r[6] * 100, r[7] * 100, r[8] * 100, r[9] * 100, 'O' if r[10] else '-', '  (제외: 접촉)' if (r[0], r[1]) in excl else ''))
for kd in ('spin', 'mid', 'pivot'):
    v = [r[9] * 100 for r in R if r[2] == kd and (r[0], r[1]) not in excl]
    if v: print('%-5s n=%2d  90°당 중앙 %.1f cm (범위 %.1f~%.1f)' % (kd, len(v), np.median(v), min(v), max(v)))
ax = [r[6] * 100 for r in R if (r[0], r[1]) not in excl and not math.isnan(r[6])]
print('회전축 앞뒤 위치(전체 ≥45° 회전) 중앙 %+.1f cm, 사분위 %+.1f~%+.1f' % (np.median(ax), *np.percentile(ax, [25, 75])))
for kd in ('spin', 'pivot'):
    a = [r[7] * 100 * (1 if r[5] > r[4] else -1) for r in R if r[2] == kd and (r[0], r[1]) not in excl]
    print('%s 회전축 좌우(느린 트랙 쪽 +) 중앙 %+.1f cm (범위 %+.1f~%+.1f)  — 기하 트랙 중심선 12.25 cm' % (kd, np.median(a), min(a), max(a)))
np.save('rot2_large.npy', np.array([(r[3], r[4], r[5], r[6], r[7], r[8], r[9], {'spin': 0, 'mid': 1, 'pivot': 2}[r[2]], (r[0], r[1]) in excl, r[0] == 'f2e2' and r[1] in (160, 163)) for r in R], float))
