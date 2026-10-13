#!/usr/bin/env python3
"""(10-13 §9) /tmp/sweep 의 시뮬 결과 요약표 — 계산만. 내용 없는 파일은 끝부분을 보여 준다."""
BAD = []
import glob, re, numpy as np, collections
R = collections.defaultdict(list)
for f in sorted(glob.glob('/tmp/sweep/*_*_*.txt')):
    sc, w, sd = re.match(r'.*/(\w+)_([0-9.]+)_(\d+)\.txt', f).groups(); s = open(f, errors='replace').read()
    m1 = re.search(r'LETHAL 여유.*?최소 (-?[0-9.]+|nan)', s); m2 = re.search(r'실패\) 주기 (\d+) 회', s); m3 = re.search(r'후: 전진 ([+-][0-9.]+)', s); m4 = re.search(r'끝 3 s 이동 ([0-9.]+)', s)
    if not (m1 and m2 and m3):
        BAD.append((f, s[-200:].replace(chr(10), ' | '))); continue
    R[(sc, float(w))].append((int(sd), float(m1.group(1)) * 100, int(m2.group(1)), float(m3.group(1)), float(m4.group(1)) if m4 else float('nan')))
print('장면         cost_w   최소 여유(cm) 중앙 · 최악 · 씨앗별(오름차순)                         멈춘 씨앗(실패≥10)   전진 거리 중앙(m)')
for (sc, w), v in sorted(R.items()):
    c = sorted(x[1] for x in v); st = [x[0] for x in v if x[2] >= 10]
    print('%-12s %5.2f    %5.1f · %5.1f · %s   %d / %d %s   %.2f' % (sc, w, np.median(c), c[0], ' '.join('%.1f' % x for x in c), len(st), len(v), ('(씨앗 %s)' % ','.join(map(str, st))) if st else '', np.median([x[3] for x in v])))
print('해석 실패 %d 개' % len(BAD))
for f, t in BAD[:3]: print('  ', f, '::', t)
import collections as _c; print('  장면별:', dict(_c.Counter(f.split('/')[-1].rsplit('_', 2)[0] for f, _ in BAD)))
