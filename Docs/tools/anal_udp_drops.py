# 10-12 §9.2: UDP 손실 시간순 분석. 인자: net_<이름>.log 포화시작(HH:MM:SS)
#   SNMP 줄 = 커널 누적(Udp: InDatagrams NoPorts InErrors OutDatagrams RcvbufErrors ...), SOCK 줄 = 소켓별 누적 drops, MAP 줄 = inode → pid·프로세스
import sys, time, collections, numpy as np
DAY = time.strftime('%Y-%m-%d ', time.localtime(next(int(l.split()[0]) for l in open(sys.argv[1], errors='replace') if l[:1].isdigit())))   # 날짜는 기록 첫 줄에서(10-13: 10-12 고정값 제거)
def ep(s): return time.mktime(time.strptime(DAY + s, '%Y-%m-%d %H:%M:%S'))
T = ep(sys.argv[2]); snmp = []; sock = collections.defaultdict(list); mp = {}
for l in open(sys.argv[1], errors='replace'):
    f = l.split()
    if not f: continue
    if f[0] == 'MAP' and len(f) >= 4: mp[f[1]] = f[3]
    elif len(f) > 3 and f[1] == 'SNMP': snmp.append((int(f[0]), int(f[3]), int(f[7])))     # t, InDatagrams, RcvbufErrors
    elif len(f) >= 5 and f[1] == 'SOCK': sock[(f[2].split(':')[-1], f[4])].append((int(f[0]), int(f[3])))
snmp = np.array(snmp, float)
def rate(a, b, col):
    k = (snmp[:, 0] >= a) & (snmp[:, 0] <= b); s = snmp[k]
    return (s[-1, col] - s[0, col]) / (s[-1, 0] - s[0, 0]) if len(s) > 1 else float('nan')
print('포화 시작 %s 기준 커널 UDP(초당): 수신 / 수신 버퍼 부족 손실 / 손실 비율' % sys.argv[2])
for nm, a, b in (('시작~T−30 s', snmp[0, 0], T - 30), ('T−30~T', T - 30, T), ('T~T+30', T, T + 30), ('T+30~끝', T + 30, snmp[-1, 0])):
    r1, r2 = rate(a, b, 1), rate(a, b, 2); print('  %-12s %8.0f / %7.0f / %5.1f %%' % (nm, r1, r2, 100 * r2 / max(r1 + r2, 1)))
pre, post = rate(T - 30, T, 2), rate(T, T + 30, 2); print('  → 손실률 T 뒤 30 s / 앞 30 s = %.1f 배' % (post / max(pre, 1e-9)))
print('10 s 칸 초당 손실: ' + ' '.join('%s %.0f' % (time.strftime('%M:%S', time.localtime(t)), rate(t, t + 10, 2)) for t in np.arange(snmp[0, 0], snmp[-1, 0] - 9, 10)))
# 소켓별: T 앞 60 s 와 T 뒤 60 s 의 초당 손실, 프로세스 이름·포트 종류(짝수 = 탐색·메타, 홀수 = 사용자 데이터, 7400/7401 = 멀티캐스트)
def srate(v, a, b):
    w = [x for x in v if a <= x[0] <= b]; return (w[-1][1] - w[0][1]) / (w[-1][0] - w[0][0]) if len(w) > 1 and w[-1][0] > w[0][0] else 0.0
rows = []
for (port, ino), v in sock.items():
    p = int(port, 16); kind = '멀티캐스트' if p in (7400, 7401) else ('사용자 데이터' if p % 2 else '메타(탐색·생존)')
    rows.append((srate(v, T, T + 60), srate(v, T - 60, T), mp.get(ino, '?'), p, kind))
agg = collections.defaultdict(lambda: [0.0, 0.0])
for post_, pre_, name, p, kind in rows: agg[(name, kind)][0] += pre_; agg[(name, kind)][1] += post_
print('프로세스·포트 종류별 초당 손실(T 앞 60 s → 뒤 60 s), 뒤 기준 상위:')
for (name, kind), (a, b) in sorted(agg.items(), key=lambda kv: -kv[1][1])[:16]: print('  %-18s %-14s %8.1f → %8.1f' % (name, kind, a, b))
tot0 = sum(v[0] for v in agg.values()); tot1 = sum(v[1] for v in agg.values()); print('  소켓 합계 %.0f → %.0f /s (커널 값과 비교용)' % (tot0, tot1))
