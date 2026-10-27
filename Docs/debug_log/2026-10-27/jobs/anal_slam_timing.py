#!/usr/bin/env python3
"""anal_slam_timing — §29 계측판 SLAM 로그('[ROVER_T]')에서 처리 스캔마다 단계별 시간(ms) 분포 (2026-10-27, PC).
  줄 묶기: AE chain → AE near → PL(match · vertex · edges · loop · buffer · total) → AS proc → CB(odom · add). 인자: 로그"""
import sys, re
import numpy as np
rows = []; cur = {}
for l in open(sys.argv[1], encoding='utf-8', errors='replace'):
    if '[ROVER_T]' not in l: continue
    for k, v in re.findall(r'(\w+)=([-\d.]+)', l.split('[ROVER_T]')[1]):
        tag = l.split('[ROVER_T]')[1].split()[0]
        cur['%s.%s' % (tag, k)] = float(v)
    if ' CB ' in l: rows.append(cur); cur = {}
keys = ['CB.add', 'AS.proc', 'PL.total', 'PL.match', 'PL.vertex', 'PL.edges', 'AE.chain', 'AE.near', 'PL.loop', 'PL.buffer', 'CB.odom']
print('처리한 스캔 %d 개 (단위 ms)' % len(rows))
print('%-10s %8s %8s %8s %8s %8s  %s' % ('단계', '중앙', '90%', '최대', '합(s)', '몫%', '설명'))
D = {'CB.add': 'addScan 전체', 'AS.proc': 'ProcessLocalization', 'PL.total': '〃(안쪽)', 'PL.match': '순차 정합', 'PL.vertex': 'AddVertex', 'PL.edges': 'AddEdges',
     'AE.chain': ' └ LinkChainToScan', 'AE.near': ' └ LinkNearChains', 'PL.loop': 'TryCloseLoop', 'PL.buffer': '버퍼 정리(노드 제거)', 'CB.odom': 'odom 조회 등'}
tot = sum(r.get('CB.add', 0) for r in rows)
for k in keys:
    v = np.array([r[k] for r in rows if k in r])
    if not len(v): continue
    print('%-10s %8.1f %8.1f %8.1f %8.2f %7.0f   %s' % (k, np.median(v), np.percentile(v, 90), v.max(), v.sum() / 1000, 100 * v.sum() / tot, D[k]))
big = [r for r in rows if r.get('CB.add', 0) > 300]
print('addScan > 300 ms 인 스캔 %d 개 — 그 스캔들의 단계 평균(ms):' % len(big))
for k in keys[3:]:
    v = [r[k] for r in big if k in r]
    if v: print('   %-10s %.1f' % (k, np.mean(v)))
