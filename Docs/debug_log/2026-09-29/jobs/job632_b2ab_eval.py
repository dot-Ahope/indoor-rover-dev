#!/usr/bin/env python3
"""B2·B3 오프라인 A/B 판정 (2026-09-29 §1): job630 출력(b2ab_all.txt)을 읽어 회전마다
   EKF 가 본 중심 이동과 스캔 직접 정합 이동(정답, 09-28 j626 의 d)의 차를 설정별로 비교한다.
   인자: b2ab_all.txt 경로"""
import re, sys, math, statistics as st

# 정답: 09-28 outputs/j626_icrfit.txt 의 d(시작 차체 기준 중심 이동, cm) — bag 안 회전 순서대로
TRUTH = {
    's1': [(-10.9, 13.0), (-8.9, 13.0), (-4.3, 9.6)],
    'r1': [(-6.6, 9.3)],
    'r1b': [(-6.7, 10.9), (-4.6, 12.6), (-1.1, 6.0)],
    'r2': [(-8.6, 9.4)],                     # 부분 회전 105°
    'r2b': [(-8.8, 10.3), (-6.4, 9.7), (-3.4, 10.0), (-3.4, 9.8)],
    'r3': [(-9.2, -13.3), (-9.9, -25.3), (-10.0, -18.4), (-5.5, -22.8)],
    's2': [(4.5, -15.4)],
}
PARTIAL = {('r2', 1)}

txt = open(sys.argv[1], encoding='utf-8').read()
res = {}   # (bag, V) -> [(x, y, lx, ly)] cm
cur = None
for line in txt.splitlines():
    m = re.match(r'== /tmp/bag_(\w+) / 설정 (\w+)', line)
    if m: cur = (m.group(1), m.group(2)); res[cur] = []; continue
    m = re.search(r'회전 (\d+): EKF 중심 이동\(앞\+/왼\+\) \(([-+.\d]+), ([-+.\d]+)\) m.*라이브 EKF \(([-+.\d]+), ([-+.\d]+)\)', line)
    if m and cur: res[cur].append(tuple(float(v) * 100 for v in m.groups()[1:]))

rows = {}
print('%-5s %2s | %-15s | %-15s | %-17s | %-17s | %-17s' % ('bag', '#', '정답', '라이브 EKF', 'off (오차)', 'b2 (오차)', 'b23 (오차)'))
for bag, tr in TRUTH.items():
    for i, (tx, ty) in enumerate(tr):
        k = (bag, i + 1); r = {}
        for V in ('off', 'b2', 'b23'):
            a = res.get((bag, V), [])
            if i < len(a): r[V] = a[i]
        if not r: continue
        rows[k] = r
        e = lambda v: math.hypot(v[0] - tx, v[1] - ty)
        live = next(iter(r.values()))[2:]
        cells = ['(%+5.1f,%+5.1f) %4.1f' % (r[V][0], r[V][1], e(r[V])) if V in r else '-' for V in ('off', 'b2', 'b23')]
        print('%-5s %2d | (%+5.1f,%+5.1f)   | (%+5.1f,%+5.1f)   | %s | %s | %s%s' % (bag, i + 1, tx, ty, live[0], live[1], *cells, '  (부분)' if k in PARTIAL else ''))

full = [k for k in rows if k not in PARTIAL]
def err(V, ks): return [math.hypot(rows[k][V][0] - TRUTH[k[0]][k[1] - 1][0], rows[k][V][1] - TRUTH[k[0]][k[1] - 1][1]) for k in ks if V in rows[k]]

v0 = [math.hypot(rows[k]['off'][0] - rows[k]['off'][2], rows[k]['off'][1] - rows[k]['off'][3]) for k in rows if 'off' in rows[k]]
print('\nV0 재생 타당성: off 재생 vs 라이브 EKF 차 중앙값 %.2f cm (최대 %.2f, n=%d) → %s' % (st.median(v0), max(v0), len(v0), '통과' if st.median(v0) <= 1.0 else '불통과'))
med = {}
for V in ('off', 'b2', 'b23'):
    E = err(V, full)
    if not E: continue
    med[V] = st.median(E)
    print('%-4s 완전 회전 n=%d: 오차 중앙값 %.1f cm, 평균 %.1f, 최대 %.1f, ≤7 cm %d/%d' % (V, len(E), med[V], st.mean(E), max(E), sum(x <= 7 for x in E), len(E)))
    for d, lab in ((1, '시계'), (-1, '반시계')):
        Ed = err(V, [k for k in full if (TRUTH[k[0]][0][1] > 0) == (d > 0)])
        if Ed: print('      %s n=%d 중앙값 %.1f cm' % (lab, len(Ed), st.median(Ed)))
    Ep = err(V, list(PARTIAL))
    if Ep: print('      부분 105°: %.1f cm' % Ep[0])
if 'b2' in med and 'off' in med:
    E = err('b2', full)
    ok = med['b2'] <= 7 and med['b2'] <= 0.5 * med['off'] and sum(x <= 7 for x in E) >= 12
    print('V1 b2 효과: 중앙값 %.1f cm (off 의 %.0f %%), ≤7 cm %d/%d → %s' % (med['b2'], 100 * med['b2'] / med['off'], sum(x <= 7 for x in E), len(E), '통과' if ok else '불통과'))
if 'b23' in med and 'b2' in med:
    print('V2 b23 무해: b23 − b2 중앙값 차 %+.1f cm → %s' % (med['b23'] - med['b2'], '통과' if med['b23'] - med['b2'] <= 1.0 else '불통과'))
