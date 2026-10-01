# 10-01 §8.9: 러너 proc_<NAME>.log(2 s 마다 전체 프로세스 CPU 틱) → 구간별 프로세스 CPU·코어 평균. 인자: LOG [시작 epoch] [끝 epoch]
import sys, collections
L = open(sys.argv[1], errors='replace').read().splitlines()
a = int(sys.argv[2]) if len(sys.argv) > 2 else 0; b = int(sys.argv[3]) if len(sys.argv) > 3 else 1 << 40
snap = collections.OrderedDict()
for l in L:
    p = l.split(None, 3)
    if len(p) < 3: continue
    t = int(p[0]); snap.setdefault(t, {})
    if p[1] == 'ALL': snap[t]['ALL'] = list(map(int, p[2:][0].split()[1:] + (p[3].split() if len(p) > 3 else [])))
    else: snap[t][p[1]] = (int(p[2]), p[3] if len(p) > 3 else '?')
ts = [t for t in snap if a <= t <= b and 'ALL' in snap[t]]
t0, t1 = ts[0], ts[-1]; s0, s1 = snap[t0], snap[t1]; dt = t1 - t0
d = [y - x for x, y in zip(s0['ALL'], s1['ALL'])]; tot = sum(d)
print('구간 %d s: 코어 평균 사용 %.0f %% · us %.0f · sy %.0f · irq+soft %.0f' % (dt, (1 - (d[3] + d[4]) / tot) * 100, d[0] / tot * 100, d[2] / tot * 100, (d[5] + d[6]) / tot * 100))
rows = []
for pid, (tk, name) in s1.items():
    if pid == 'ALL' or pid not in s0: continue
    rows.append(((tk - s0[pid][0]) / dt, name, pid))
for c, name, pid in sorted(rows, reverse=True)[:25]:
    if c >= 2: print('%6.1f %%  %-7s %s' % (c, pid, name))
