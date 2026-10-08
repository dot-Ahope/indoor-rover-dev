# 10-08 §5 비율 시험 분석(PC): 회전마다 정지 스캔끼리 직접 정합(실제 이동) − 휠 추측항법 = 미끄러짐. rot2.py 와 같은 잣대.
#   회전 = 0 이 아닌 /cmd_vel 이 이어진 구간(앞뒤 0 지령 ≥ 1 s). 시작 정지 스캔 = 지령 직전 0.5 s 안 마지막 스캔, 끝 = 지령 끝 + 3 s 스캔.
#   잡음 바닥 = 정지 중 1 s 떨어진 스캔끼리 정합한 이동(회전마다 1 개).
#   인자: bag... → 표 + ratio_<bag>.csv
import math, re, sys, csv, numpy as np
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent)); BAGS = sys.argv[1:]
from rot2 import load, pts, icp   # rot2.py 의 읽기·정합 함수(같은 폴더)

for bag in BAGS:
    S, C, ST = load(bag); st = np.array([s[0] for s in S]); name = Path(bag).name
    nz = (np.abs(C[:, 1]) > 1e-4) | (np.abs(C[:, 2]) > 1e-4); segs = []; s = None
    for i in range(len(C)):
        if nz[i] and s is None: s = i
        if not nz[i] and s is not None:
            if C[i - 1, 0] - C[s, 0] > 1.0: segs.append((s, i - 1))
            s = None
    out = []
    for i0, i1 in segs:
        a, b = C[i0, 0], C[i1, 0]; v, w = np.median(C[i0:i1 + 1, 1]), np.median(C[i0:i1 + 1, 2])
        F, Bh = 0.08, 0.2215; r = round((abs(v) - abs(w) * Bh) / (abs(v) + abs(w) * Bh), 1)   # 지령에서 비율 복원
        j0 = np.searchsorted(st, a) - 1; j1 = np.searchsorted(st, b + 3.0); jn = np.searchsorted(st, a - 1.0) - 1
        if j0 < 1 or j1 >= len(S) or jn < 0: continue
        idx = list(range(j0, j1 + 1)); X = [np.zeros(3)]; Pp = pts(S[j0])
        for k0, k1 in zip(idx[:-1], idx[1:]):
            kc = (C[:, 0] >= S[k0][0] - 0.2) & (C[:, 0] < S[k1][0]); P1 = pts(S[k1])
            th, t, _ = icp(Pp, P1, C[kc, 2].mean() * (S[k1][0] - S[k0][0]) if kc.any() else 0)
            x, y, h = X[-1]; c, sn = math.cos(h), math.sin(h); X.append(np.array([x + c * t[0] - sn * t[1], y + sn * t[0] + c * t[1], h + th])); Pp = P1
        X = np.array(X); th, t, rms = icp(pts(S[j0]), pts(S[j1]), X[-1, 2], X[-1, :2])   # 끝↔시작 직접(사슬은 초기값·방향용)
        T = st[idx]; vl = np.interp(T, ST[:, 0], ST[:, 2]) / 1000; vr = np.interp(T, ST[:, 0], ST[:, 5]) / 1000
        vl, vr = np.where(np.interp(T, ST[:, 0], ST[:, 1]) < 0, -np.abs(vl), np.abs(vl)), np.where(np.interp(T, ST[:, 0], ST[:, 4]) < 0, -np.abs(vr), np.abs(vr))   # FG 는 방향이 없음 → 목표 부호
        D = np.zeros(2)
        for k in range(len(T) - 1):
            h = (X[k, 2] + X[k + 1, 2]) / 2; D += (vl[k] + vr[k]) / 2 * (T[k + 1] - T[k]) * np.array([math.cos(h), math.sin(h)])
        E = t - D; _, tn, _ = icp(pts(S[jn]), pts(S[j0]), 0.0)
        k = (ST[:, 0] >= a + 0.5) & (ST[:, 0] <= b)
        out.append(dict(t=a - S[0][0], r=r, dir=int(np.sign(w)), fwd=int(np.sign(v)) if abs(v) > 1e-3 else 0, v=v, w=w, rot=math.degrees(th),
                        mx=t[0], my=t[1], wx=D[0], wy=D[1], ex=E[0], ey=E[1], slip=math.hypot(*E), slip90=math.hypot(*E) * 90 / max(abs(math.degrees(th)), 1),
                        L=np.abs(ST[k, 2]).mean() / 1000, R=np.abs(ST[k, 5]).mean() / 1000, rms=rms, noise=math.hypot(*tn)))
    print('== %s  회전 %d 개' % (name, len(out)))
    print('  t s   r    방향 앞뒤 | 회전° | 실제 이동 앞 왼 | 휠 앞 왼 | 미끄러짐 앞 왼 = 크기 (90°당) cm | |L| |R| m/s | rms · 잡음 cm')
    for o in out:
        print('  %5.0f %+.1f %s %s | %+6.1f | %+5.1f %+5.1f | %+5.1f %+5.1f | %+5.1f %+5.1f = %4.1f (%4.1f) | %.3f %.3f | %.3f · %.1f' % (
            o['t'], o['r'], '시계' if o['dir'] < 0 else '반시', {1: '앞', -1: '뒤', 0: '-'}[o['fwd']], o['rot'], o['mx'] * 100, o['my'] * 100, o['wx'] * 100, o['wy'] * 100,
            o['ex'] * 100, o['ey'] * 100, o['slip'] * 100, o['slip90'] * 100, o['L'], o['R'], o['rms'], o['noise'] * 100))
    print('  -- 조건별 90°당 미끄러짐(cm): 중앙 [범위] n')
    for key in sorted({(o['r'], o['dir'], o['fwd']) for o in out}):
        vv = [o['slip90'] * 100 for o in out if (o['r'], o['dir'], o['fwd']) == key]
        print('  r %+.1f %s %s: %4.1f [%4.1f~%4.1f] n %d' % (key[0], '시계' if key[1] < 0 else '반시', {1: '앞', -1: '뒤', 0: '-'}[key[2]], np.median(vv), min(vv), max(vv), len(vv)))
    for rr in sorted({o['r'] for o in out}):
        vv = [o['slip90'] * 100 for o in out if o['r'] == rr]   # §5.1: r 마다 전체(방향·앞뒤 2 회씩) n 8
        if not vv: continue
        fa = [o['slip90'] * 100 for o in out if o['r'] == rr and o['fwd'] > 0]; ba = [o['slip90'] * 100 for o in out if o['r'] == rr and o['fwd'] < 0]
        print('  r %+.1f 전체: %4.1f [%4.1f~%4.1f] n %d | 앞 %s · 뒤 %s' % (rr, np.median(vv), min(vv), max(vv), len(vv),
              '%.1f (n %d)' % (np.median(fa), len(fa)) if fa else '-', '%.1f (n %d)' % (np.median(ba), len(ba)) if ba else '-'))
    if out:
        print('  잡음 바닥 중앙 %.1f cm, 최대 %.1f · 정합 rms 최대 %.3f m' % (np.median([o['noise'] for o in out]) * 100, max(o['noise'] for o in out) * 100, max(o['rms'] for o in out)))
        with open('ratio_%s.csv' % name, 'w', newline='') as f:
            c = csv.DictWriter(f, fieldnames=list(out[0])); c.writeheader(); c.writerows(out)
