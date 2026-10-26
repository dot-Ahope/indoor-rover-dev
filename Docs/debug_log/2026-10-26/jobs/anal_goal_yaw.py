#!/usr/bin/env python3
"""anal_goal_yaw — §20 목표 방향 시험 결과 표 (2026-10-26, PC, 로버 안 움직임).
  입력: 결과.npz(query_planners) 장면.npz(prep_scenes). 장면 이름 = sa3_<순간>_d<방향 더하기>.
  순간 × 방향마다: Smac 성공 · 계획 시간 · 실패 문구, NavFn 성공, 목표 자세 차체(+ 패딩 0.01) 아래 치명(100) · 내접(99) 칸 수(재구성 지도),
    출발 자세 차체 아래 치명 칸 수(같은 방식). 차체 표본 = 칸 절반 간격 격자(§19 chk_smac_fail_cells 와 같은 정의).
  판정(§20 선언): ① 원래 방향(+0) 재현 ② (a) 목표 치명 > 0 이면 Smac 모두 실패 (b) 실패 3 순간에 치명 0 방향 성공 ③ 나머지 2 순간 방향별 결과.
  인자: 결과.npz 장면.npz"""
import sys, json, math, re
import numpy as np
R = np.load(sys.argv[1]); SC = np.load(sys.argv[2]); meta = json.loads(str(SC['meta']))
V = 'Smac_R10_C30_A10_RS'; FP = (0.262 + 0.01, -0.248 - 0.01, 0.165 + 0.01)
LIVE = {'115653': '실패', '121553': '실패', '122202': '실패', '123521': '실패', '125954': '실패', '130865': '성공'}


def under(G, info, x, y, yaw):
    ox, oy, r, _ = info; c, s = math.cos(yaw), math.sin(yaw); v = []
    for u in np.arange(FP[1], FP[0] + 1e-9, r / 2):
        for w in np.arange(-FP[2], FP[2] + 1e-9, r / 2):
            i, j = int((y + s * u + c * w - oy) / r), int((x + c * u - s * w - ox) / r)
            v.append(G[i, j] if 0 <= i < G.shape[0] and 0 <= j < G.shape[1] else 100)
    v = np.array(v); return int((v == 100).sum()), int((v == 99).sum())


rows = {}
for sc in meta:
    k = sc['name']; m = re.match(r'sa3_(\d+)_d([+-]\d+)', k); tag, off = m.group(1), int(m.group(2))
    if k + '/recon' not in R: rows.setdefault(tag, []).append((off, None)); continue
    G = R[k + '/recon'].astype(np.int16); info = SC[k + '/info']; st = SC[k + '/start']; gl = SC[k + '/goal']
    sp = R.get('%s/%s/path' % (k, V)); ok = sp is not None and len(sp) > 0
    t = R['%s/%s/t' % (k, V)] if '%s/%s/t' % (k, V) in R else [-1, -1, -1]
    msg = str(R['%s/%s/msg' % (k, V)]) if '%s/%s/msg' % (k, V) in R else ''
    nf = R.get('%s/GridBased/path' % k); nok = nf is not None and len(nf) > 0
    rows.setdefault(tag, []).append((off, dict(ok=ok, t=float(t[0]), msg=msg, nav=nok, gl=under(G, info, *gl), st=under(G, info, *st),
                                               gyaw=math.degrees(gl[2]), L=float(np.hypot(*np.diff(sp[:, :2], axis=0).T).sum()) if ok else 0.0)))
short = lambda s: ('출발 치명' if 'Starting point' in s else '목표 치명' if 'Goal' in s or 'goal' in s else '해 없음' if 'no valid path' in s else '시간 초과' if 'time' in s.lower() else s[:40]) if s else ''
print('Smac = %s(시간 상한 2.0 s) · 치명 = 차체(+0.01) 아래 100 칸 수 · 내접 = 99 칸 수(재구성 지도)' % V)
A_bad, B = [], {}
for tag in LIVE:
    R_ = sorted(rows.get(tag, []), key=lambda q: (abs(q[0]), q[0]))
    d0 = dict(R_).get(0)
    print('\n== %s(실주행 %s) — 출발 차체 치명 %s' % (tag, LIVE[tag], d0['st'][0] if d0 else '?'))
    print('  방향 더하기 | 목표 yaw | 목표 치명 · 내접 | Smac | 시간 s | 길이 m | 실패 문구 | NavFn')
    for off, d in R_:
        if d is None: print('  %+4d | 재구성 실패' % off); continue
        print('  %+4d | %5.0f° | %3d · %3d | %s | %.3f | %.2f | %s | %s' % (off, d['gyaw'], *d['gl'], '성공' if d['ok'] else '실패', d['t'], d['L'], short(d['msg']), '성공' if d['nav'] else '실패'))
        if d['ok'] and d['gl'][0] > 0: A_bad.append((tag, off, d['gl'][0]))
        B.setdefault(tag, []).append((off, d['ok'], d['gl'][0]))
print('\n== 판정')
rep = [(t, LIVE[t], ('성공' if dict(rows[t]).get(0) and dict(rows[t])[0]['ok'] else '실패')) for t in LIVE if t in rows]
print('① 재현(+0): ' + ' · '.join('%s 실주행 %s / 오프라인 %s%s' % (t, a, b, '' if a == b else ' ✘') for t, a, b in rep))
print('② (a) 목표 치명 > 0 인데 Smac 성공: %d 건 %s' % (len(A_bad), A_bad[:10]))
for tag in ('121553', '122202', '125954', '115653', '123521'):
    L = B.get(tag, []); free = [o for o, ok, c in L if c == 0]; okfree = [o for o, ok, c in L if c == 0 and ok]
    print('   %s: 목표 치명 0 방향 %s · 그중 Smac 성공 %s' % (tag, free, okfree))
tot = [(ok, c > 0) for L in B.values() for _, ok, c in L]
for blocked in (True, False):
    sel = [ok for ok, b in tot if b == blocked]
    print('   목표 치명 %s: Smac 성공 %d / %d' % ('> 0' if blocked else '= 0', sum(sel), len(sel)))
