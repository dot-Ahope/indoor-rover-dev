#!/usr/bin/env python3
"""anal_pba_replay_extend — (10-23 §20.7) only_new 로 막힘을 안 셌다면 그 경로를 목표 도착까지 계속 썼을 것: f2rp3 경로 #3(14:47:09 서쪽 통로)을
  다음 경로가 아니라 목표 도착(14:47:43.57)까지 이어 판정. 로버 자세는 실제 기록(옛 동작으로 지나간 길 — 근사). 인자: bag nav2.log"""
import sys, numpy as np
src = open(__file__.replace('_extend', ''), encoding='utf-8').read().split("print('입력")[0]
g = {}; exec(compile(src, 'anal_pba_replay', 'exec'), g)
at, MO, MOt, OB, OBt, GR, GRt, comp, cost, paths, hm = [g[n] for n in 'at MO MOt OB OBt GR GRt comp cost paths hm'.split()]
tp, P, _ = paths[3]; tend = 1792734463.57; init = cost(at(GR, GRt, tp), P); since = None; t = tp; worst = 0; fired = None
while t < tend:
    p = comp(at(MO, MOt, t)[1], at(OB, OBt, t)[1]); q = np.array(p[:2]); i0 = int(np.argmin(np.linalg.norm(P - q, axis=1)))
    s = np.r_[0, np.cumsum(np.linalg.norm(np.diff(P[i0:], axis=0), axis=1))]; idx = i0 + np.nonzero((s >= 0.30) & (s <= 1.5))[0]
    c = cost(at(GR, GRt, t), P[idx]); hit = (c >= 99) & (c > init[idx])
    if hit.any():
        since = t if since is None else since; worst = max(worst, t - since)
        if t - since >= 2.0 - 1e-6 and fired is None: fired = (t, P[idx[np.argmax(hit)]])
    else: since = None
    t += 0.02
print('경로 #3 받은 %s · 그 경로 점 %d 개 중 받을 때 이미 ≥ 99 인 점 %d 개' % (hm(tp), len(P), int((init >= 99).sum())))
print('only_new 로 %s 까지 이어 판정: 가장 긴 연속 막힘 %.2f s → %s' % (hm(tend), worst, ('막힘 중단 %s (%.2f, %.2f)' % (hm(fired[0]), *fired[1])) if fired else '막힘 중단 없음'))
