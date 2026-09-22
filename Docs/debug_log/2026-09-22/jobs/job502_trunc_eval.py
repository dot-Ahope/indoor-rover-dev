#!/usr/bin/env python3
"""09-22 §1 절단 A/B 평가: STVL(stvl3) / t4 / t2 의 job489 JSON(base_link, 5 cm)을 공통 격자에 스냅해 T1~T4·T6 를 센다(T5 는 job474·tegrastats 출력에서 읽음).
  사용: python job502_trunc_eval.py <dir> [BX]   — dir 에 grid_stvl3_costmap.json, grid_t{4,2}_{costmap,slice}.json
"""
import json, math, collections, sys, os
R = 0.05
D = sys.argv[1] if len(sys.argv) > 1 else '.'
BX = float(sys.argv[2]) if len(sys.argv) > 2 else 1.153
def snap(x): return int(math.floor(x / R))
def load(f): return {(snap(c[0]), snap(c[1])): c[2] for c in json.load(open(os.path.join(D, f), encoding='utf-8'))['cells']}
def region(k):
    x, y = (k[0] + 0.5) * R, (k[1] + 0.5) * R
    if 0.9 < x < 1.5 and -0.35 < y < 0.15: return '상자'
    if y < -0.5: return '우측 벽'
    if y > 0.45: return '좌측 가구'
    if x < 0.3: return '뒤·옆'
    return '기타'
def ext(cells):
    if not cells: return ('없음', None, None, None)
    xs = [c[0] for c in cells]; ys = [c[1] for c in cells]
    return ('x %.2f~%.2f, y %+.2f~%+.2f (%d)' % (min(xs) * R, (max(xs) + 1) * R, min(ys) * R, (max(ys) + 1) * R, len(cells)), min(xs) * R, (max(xs) + 1) * R, (max(ys) + 1) * R)
S = load('grid_stvl3_costmap.json'); lethS = {k for k, v in S.items() if v >= 100}
res = {}
for nm in ('t4', 't2'):
    N = load('grid_%s_costmap.json' % nm); L = load('grid_%s_slice.json' % nm)
    lethN = {k for k, v in N.items() if v >= 100}; lethL = {k for k, v in L.items() if v is not None and v <= 0}
    both = lethS & lethN; nonly = lethN - lethS; sonly = lethS - lethN
    regN = collections.Counter(region(k) for k in nonly)
    boxL = [k for k in lethL if region(k) == '상자']; boxN = [k for k in lethN if region(k) == '상자']
    eL = ext(boxL); eN = ext(boxN)
    # T6: 구역별 LETHAL 을 가진 x 열(5 cm) 수 — 슬라이스 기준(층은 라이다가 섞임)
    cols = {r: len({k[0] for k in lethL if region(k) == r}) for r in ('우측 벽', '좌측 가구')}
    rows = {r: len({k[1] for k in lethL if region(k) == r}) for r in ('우측 벽', '좌측 가구')}
    res[nm] = dict(lethN=len(lethN), lethL=len(lethL), both=len(both), nonly=len(nonly), sonly=len(sonly), regN=dict(regN), boxL=eL, boxN=eN, cols=cols, rows=rows, front=eL[1], depth=(eL[2] - eL[1]) if eL[1] is not None else None)
print('STVL(stvl3) LETHAL %d, 상자 %s' % (len(lethS), ext([k for k in lethS if region(k) == '상자'])[0]))
for nm in ('t4', 't2'):
    r = res[nm]
    print('== %s: 층 LETHAL %d / 슬라이스 ≤0 %d | 둘 다 %d / nvblox 만 %d %s / STVL 만 %d' % (nm, r['lethN'], r['lethL'], r['both'], r['nonly'], r['regN'], r['sonly']))
    print('   상자 — 층 %s | 슬라이스 %s | 앞면 셀 %.2f(물리 %.3f) 깊이 %.2f m' % (r['boxN'][0], r['boxL'][0], r['front'], BX, r['depth']))
    print('   표면 연속성(슬라이스, LETHAL 가진 x 열 / y 행): 우측 벽 %d/%d, 좌측 가구 %d/%d' % (r['cols']['우측 벽'], r['rows']['우측 벽'], r['cols']['좌측 가구'], r['rows']['좌측 가구']))
t4, t2 = res['t4'], res['t2']
T1 = t4['front'] == t2['front'] and abs(t2['front'] - math.floor(BX / R) * R) < 1e-9
T2 = t2['depth'] is not None and t2['depth'] <= 0.15 + 1e-9
T3 = t2['nonly'] <= 0.6 * t4['nonly'] and t2['sonly'] <= 10
# T6: 우측 벽은 x 열(벽이 x 방향으로 뻗음), 좌측 가구는 x 열 기준 — 4.0 대비 10 % 이상 감소 금지
def keep(a, b): return b >= 0.9 * a
T6 = keep(t4['cols']['우측 벽'], t2['cols']['우측 벽']) and keep(t4['cols']['좌측 가구'], t2['cols']['좌측 가구'])
print('T1 앞면 동일·물리 셀: %s (t4 %.2f, t2 %.2f) | T2 깊이 ≤0.15: %s (%.2f → %.2f) | T3 nvblox만 ≥40%% 감소·STVL만 ≤10: %s (%d → %d, STVL만 %d) | T6 표면 연속성: %s (우측 벽 열 %d → %d, 좌측 가구 %d → %d)' % (
    T1, t4['front'], t2['front'], T2, t4['depth'], t2['depth'], T3, t4['nonly'], t2['nonly'], t2['sonly'], T6, t4['cols']['우측 벽'], t2['cols']['우측 벽'], t4['cols']['좌측 가구'], t2['cols']['좌측 가구']))
print('T4·T5 는 감사(j501_ab_*.txt)·job474/tegrastats 출력에서 읽는다.')
