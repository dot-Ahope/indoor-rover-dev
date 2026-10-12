# 10-12 §2: top 기록(2 s 간격)에서 구간별 부하 — load average, 유휴 %, 프로세스별 CPU 평균. 인자: top.log HH:MM:SS HH:MM:SS [..구간 더]
import sys, re, collections
blocks = []; cur = None
for l in open(sys.argv[1], errors='replace'):
    m = re.match(r'top - (\d\d:\d\d:\d\d).*load average: ([\d.]+)', l)
    if m: cur = dict(t=m.group(1), load=float(m.group(2)), idle=None, p=collections.Counter()); blocks.append(cur); continue
    if cur is None: continue
    m = re.search(r'([\d.]+) id', l)
    if l.startswith('%Cpu') and m: cur['idle'] = float(m.group(1)); continue
    f = l.split()
    if len(f) >= 12 and f[0].isdigit():
        try: cur['p'][f[11][:15]] += float(f[8])
        except ValueError: pass
for a, b in zip(sys.argv[2::2], sys.argv[3::2]):
    B = [x for x in blocks if a <= x['t'] <= b]
    if not B: print(a, b, '표본 없음'); continue
    tot = collections.Counter()
    for x in B: tot.update(x['p'])
    print('%s~%s n %d | load %.1f~%.1f | 유휴 평균 %.0f %% 최소 %.0f %% | %s' % (a, b, len(B), min(x['load'] for x in B), max(x['load'] for x in B), sum(x['idle'] or 0 for x in B) / len(B), min(x['idle'] or 0 for x in B),
          ' '.join('%s %.0f' % (k, v / len(B)) for k, v in tot.most_common(12))))
