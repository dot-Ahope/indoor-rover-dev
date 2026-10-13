#!/usr/bin/env python3
"""(10-13 §11) 패딩 0 시뮬(/tmp/sweep_pad0) 대 현재 패딩 0.01(/tmp/sweep 의 cost_w 3.81) 요약표 — 계산만."""
import glob, re, numpy as np, collections
print('장면         패딩    최소 여유(cm) 중앙 · 최악 · 씨앗별(씨앗 번호순)                          멈춘 씨앗(실패≥10)    실패 주기 합   전진 중앙(m)')
for lab, pat in (('0.01', '/tmp/sweep/%s_3.81_*.txt'), ('0', '/tmp/sweep_pad0/%s_3.81_*.txt')):
    for sc in ('box_f2o1', 'box_f2p1', 'door_f2a10', 'out_f2o1'):
        v = []
        for f in glob.glob(pat % sc):
            s = open(f, errors='replace').read(); sd = int(re.search(r'_(\d+)\.txt$', f).group(1))
            m1 = re.search(r'LETHAL 여유.*?최소 (-?[0-9.]+|nan)', s); m2 = re.search(r'실패\) 주기 (\d+) 회', s); m3 = re.search(r'후: 전진 ([+-][0-9.]+)', s)
            if m1 and m2 and m3: v.append((sd, float(m1.group(1)) * 100, int(m2.group(1)), float(m3.group(1))))
        v.sort(); c = [x[1] for x in v]; st = [x[0] for x in v if x[2] >= 10]
        print('%-12s %-5s   %5.1f · %5.1f · %s   %d / %d %s   %4d   %.2f' % (sc, lab, np.median(c), min(c), ' '.join('%.1f' % x for x in c), len(st), len(v), ('(씨앗 %s)' % ','.join(map(str, st))) if st else '        ', sum(x[2] for x in v), np.median([x[3] for x in v])))
