# 10-08 §5.6: 실행 1·2 회전을 합쳐 §5·§5.1·§5.5 판정(V·Q0·Q1·Q2·Q3) — ratio_anal.py 의 csv 를 읽음
#   빠른 트랙: |L| vs |R| 큰 쪽(r −1 은 '같음'). 구르는 방향 = 지령 v 부호(빠른 트랙은 v 와 같은 방향으로 구름).
import csv, sys, numpy as np
R = []
for f in sys.argv[1:]:
    for o in csv.DictReader(open(f, encoding='utf-8')):
        o = {k: (float(v) if k not in () else v) for k, v in o.items()}; o['src'] = f; R.append(o)
ok = [o for o in R if o['rms'] <= 0.03 and o['noise'] <= 0.01]
print('V: 회전 %d 중 유효 %d (rms ≤ 0.03, 잡음 ≤ 1 cm)' % (len(R), len(ok)))
def side(o): return '같음' if o['r'] <= -0.95 else ('왼' if o['L'] > o['R'] else '오')
def roll(o): return '-' if o['r'] <= -0.95 else ('앞' if o['v'] > 0 else '뒤')
med = lambda v: np.median(v) if v else float('nan')
spin = [o['slip90'] * 100 for o in ok if o['r'] <= -0.95]; ms = med(spin)
print('Q0: r −1 n %d 중앙 %.1f cm/90° [%.1f~%.1f] (09-28 범위 5~13.5)' % (len(spin), ms, min(spin), max(spin)))
print('\n r    | 전체 중앙 [범위] n | 빠른 왼·앞 | 왼·뒤 | 오·앞 | 오·뒤   (90°당 cm, 각 값 나열)')
best = None
for r in sorted({o['r'] for o in ok}):
    vv = [o['slip90'] * 100 for o in ok if o['r'] == r]
    cells = []
    for s_, d_ in (('왼', '앞'), ('왼', '뒤'), ('오', '앞'), ('오', '뒤')):
        c = [o['slip90'] * 100 for o in ok if o['r'] == r and side(o) == s_ and roll(o) == d_]
        cells.append(' '.join('%.1f' % x for x in c) or '-')
    print(' %+.1f | %4.1f [%4.1f~%4.1f] n %2d | %s | %s | %s | %s' % (r, med(vv), min(vv), max(vv), len(vv), *cells))
    if r > -0.95:
        below = sum(x < ms for x in vv); q1 = med(vv) <= 0.5 * ms and below >= 6
        print('       Q1: 중앙 %.1f ≤ 0.5×%.1f=%.1f? %s · r −1 중앙보다 작은 회전 %d/%d → %s' % (med(vv), ms, 0.5 * ms, med(vv) <= 0.5 * ms, below, len(vv), '충족' if q1 else '불충족'))
        if best is None or med(vv) < best[1]: best = (r, med(vv))
print('\n가장 작은 중앙(반피벗·피벗 중): r %+.1f %.1f cm' % best)
print('\nQ3 앞으로 구를 때 vs 뒤로 구를 때(빠른 트랙별, r −0.6~0 합침):')
for s_ in ('왼', '오'):
    a = [o['slip90'] * 100 for o in ok if o['r'] > -0.95 and side(o) == s_ and roll(o) == '앞']
    b = [o['slip90'] * 100 for o in ok if o['r'] > -0.95 and side(o) == s_ and roll(o) == '뒤']
    print('  빠른 %s 트랙: 앞 %.1f (n %d) · 뒤 %.1f (n %d) → %s' % (s_, med(a), len(a), med(b), len(b), '뒤가 절반 이하' if med(b) <= 0.5 * med(a) else ('앞이 절반 이하' if med(a) <= 0.5 * med(b) else '큰 차이 없음')))
