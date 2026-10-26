#!/usr/bin/env python3
"""anal_sim_corner_summary — §10.4 시뮬 70 판 요약(PC). 병렬 출력이 한 줄에 섞여도 '라벨 s씨앗 |' 경계로 나눠 셈(첫 판은 섞인 줄 1 개를 놓쳐 base n 9).  인자: 원문 txt 출력 txt"""
import re, sys, numpy as np, collections
txt = open(sys.argv[1], encoding='utf-8', errors='replace').read()
parts = re.split(r'(?=\b(?:base|A28Fw5|A28|Fw5|B2000|WZ03|IT3) s\d+ \|)', txt)
R = collections.defaultdict(list)
for p in parts:
    m = re.match(r'(\S+) s(\d+) \|.*?최대 ([-+\d.na]+) · 중앙 ([-+\d.na]+) m.*?정지 ([\d.]+) s · 평균 속도 ([\d.]+).*?첫 굽은 곳 이탈 ([-+\d.na]+) · 굽은 곳 95% ([-+\d.na]+).*?실패\) 주기 (\d+)', p, re.S)
    if m: R[m.group(1)].append([float(x) for x in m.groups()[2:]])
b = np.array(R['base'])[:, 0]
out = ['변형 | n | 안쪽 최대 평균 ± 표준편차 · 최악 (cm) | 95% 평균 | 중앙 평균 | 정지 합 s | 평균 속도 | 실패 | base 대비 평균 차 / 표준오차']
for k in ['base', 'A28', 'Fw5', 'A28Fw5', 'B2000', 'WZ03', 'IT3']:
    a = np.array(R[k]); x = a[:, 0]; se = np.sqrt(x.var(ddof=1) / len(x) + b.var(ddof=1) / len(b))
    out.append('%-7s | %2d | %5.1f ± %4.1f · %5.1f | %5.1f | %5.1f | %.1f | %.3f | %d | %+5.1f / %.1f' % (k, len(a), 100 * x.mean(), 100 * x.std(ddof=1), 100 * x.max(), 100 * a[:, 5].mean(), 100 * a[:, 1].mean(), a[:, 2].sum(), a[:, 3].mean(), a[:, 6].sum(), 100 * (x.mean() - b.mean()), 100 * se))
print('\n'.join(out)); open(sys.argv[2], 'w', encoding='utf-8').write('\n'.join(out) + '\n')
