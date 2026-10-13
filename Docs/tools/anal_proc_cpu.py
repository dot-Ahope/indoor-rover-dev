# 10-12 §3.3: 프로세스별 CPU(전 프로세스 틱 기록) 구간 비교. 인자: 이름=proc.log@시작epoch@끝epoch ...  (코어 1 개 = 100)
import sys, collections
res = {}
for a in sys.argv[1:]:
    nm, rest = a.split('='); f, A, B = rest.split('@'); A, B = int(A), int(B); snap = collections.defaultdict(dict)
    for l in open(f, errors='replace'):
        p = l.split(None, 3)
        if len(p) < 4 or p[1] == 'ALL': continue
        try: snap[int(p[0])][(p[1], p[3].strip())] = int(p[2])
        except ValueError: pass
    ts = sorted(snap); a0 = min(ts, key=lambda t: abs(t - A)); b0 = min(ts, key=lambda t: abs(t - B)); d = collections.Counter()
    for k, v in snap[b0].items():
        if k in snap[a0]: d[k[1][:22]] += (v - snap[a0][k]) / (b0 - a0)
        else: d[k[1][:22]] += v / (b0 - a0)
    res[nm] = d
names = list(res); keys = sorted(set().union(*res.values()), key=lambda k: -max(r.get(k, 0) for r in res.values()))[:26]
print('%-24s' % '프로세스' + ''.join('%14s' % n for n in names))
for k in keys: print('%-24s' % k + ''.join('%14.1f' % res[n].get(k, 0) for n in names))
print('%-24s' % '합계' + ''.join('%14.0f' % sum(res[n].values()) for n in names))
