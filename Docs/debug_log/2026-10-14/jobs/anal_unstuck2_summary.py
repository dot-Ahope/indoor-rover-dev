#!/usr/bin/env python3
"""(10-14 §2) /tmp/unstuck2 의 갇힘 해제 되돌림 시뮬 요약 — 계산만."""
import glob, re, numpy as np, collections
R = collections.defaultdict(list); bad = 0
for f in sorted(glob.glob('/tmp/unstuck2/*_*_*.txt')):
    sc, d, sd = re.match(r'.*/(\w+?)_([0-9.]+)_(\d+)\.txt', f).groups(); s = open(f, errors='replace').read()
    m1 = re.search(r'LETHAL 여유.*?최소 (-?[0-9.]+|nan)', s); m3 = re.search(r'후: 전진 ([+-][0-9.]+)', s); m5 = re.search(r'패딩 0 전환 (\d+) 회 · 패딩 0 이던 시간 ([0-9.]+) s · 되돌린 뒤 5 s 안에 다시 갇힘 (\d+) 회 · 끝날 때 패딩 (\S+) \| (.*)', s); m2 = re.search(r'실패\) 주기 (\d+) 회', s)
    if not (m1 and m3 and m5 and m2): bad += 1; print('해석 실패', f, s[-250:].replace('\n', ' | ')); continue
    R[(sc, d)].append((int(sd), float(m3.group(1)), float(m1.group(1)) * 100, int(m5.group(1)), float(m5.group(2)), int(m5.group(3)), m5.group(4), int(m2.group(1)), m5.group(5)))
print('파일 %d · 해석 실패 %d' % (len(glob.glob('/tmp/unstuck2/*_*_*.txt')), bad))
print('정지 자세  us_d   30 s 뒤 전진(m, 씨앗 1~5)          ≥1.0 m   전환 횟수(씨앗별)  패딩 0 시간(s, 씨앗별)      재갇힘 합  최소 여유 최악(cm)  끝날 때 패딩 0 인 씨앗')
for (sc, d), v in sorted(R.items()):
    v.sort(); print('%-8s %-5s  %s   %d / %d    %s        %s     %d         %5.1f             %d' % (sc, d, ' '.join('%+.2f' % x[1] for x in v), sum(x[1] >= 1.0 for x in v), len(v), ' '.join(str(x[3]) for x in v), ' '.join('%4.1f' % x[4] for x in v), sum(x[5] for x in v), min(x[2] for x in v), sum(x[6] == '0' for x in v)))
for (sc, d), v in sorted(R.items()):
    print('  예: %s us_d %s 씨앗 1 — %s' % (sc, d, v[0][8][:170]))
