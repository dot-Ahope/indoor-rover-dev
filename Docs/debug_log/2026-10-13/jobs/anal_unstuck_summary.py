#!/usr/bin/env python3
"""(10-13 §14.2) /tmp/unstuck 의 탈출 시뮬 결과 요약 — 계산만."""
import subprocess; print("파일", subprocess.run("ls /tmp/unstuck/*_*_*.txt | wc -l; pgrep -fc anal_mppi_sim.py", shell=True, capture_output=True, text=True).stdout.split())
import glob, re, numpy as np, collections
R = collections.defaultdict(list)
for f in sorted(glob.glob('/tmp/unstuck/*_*_*.txt')):
    sc, pd, sd = re.match(r'.*/(\w+?)_([0-9.]+)_(\d+)\.txt', f).groups(); s = open(f, errors='replace').read()
    m1 = re.search(r'LETHAL 여유.*?최소 (-?[0-9.]+|nan)', s); m2 = re.search(r'실패\) 주기 (\d+) 회', s); m3 = re.search(r'후: 전진 ([+-][0-9.]+) 횡 ([+-][0-9.]+) 회전 ([+-][0-9.]+)', s); m4 = re.search(r'후진 거리 ([0-9.]+)', s)
    if not (m1 and m2 and m3): print('해석 실패', f, s[-200:].replace('\n', ' | ')); continue
    R[(sc, pd)].append((int(sd), float(m3.group(1)), float(m1.group(1)) * 100, int(m2.group(1)), float(m4.group(1)), float(m3.group(3))))
print('정지 자세   패딩    15 s 뒤 전진(m, 씨앗 1~5)            나온 씨앗(≥0.30 m)   최소 여유(cm) 최악   실패 주기(/150, 씨앗별)        후진 거리(m) 중앙')
for (sc, pd), v in sorted(R.items()):
    v.sort(); print('%-8s %-5s   %s   %d / %d             %5.1f            %s     %.2f' % (sc, pd, ' '.join('%+.2f' % x[1] for x in v), sum(x[1] >= 0.30 for x in v), len(v), min(x[2] for x in v), ' '.join('%3d' % x[3] for x in v), np.median([x[4] for x in v])))
