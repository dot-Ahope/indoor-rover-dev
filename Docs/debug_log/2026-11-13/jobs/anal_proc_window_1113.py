#!/usr/bin/env python3
# anal_proc_window_1113 — 11-13 §3: 주행 proc 로그(job551 의 /tmp/proc_<이름>.log: "시각 pid 틱 명령" 2 s 마다 + "시각 ALL /proc/stat 첫 줄")에서
#   지정 시각 창의 프로세스(명령 이름)별 CPU %(코어 1 개 = 100)와 전체 사용률(6 코어 평균)을 낸다. PC, 로버 안 움직임.
#   왜: f2rd1 서쪽 통로에서 컨트롤러 주기 놓침이 f2rr1 의 약 3 배 — 기록 부하(컬러 · 깊이 SHM) 때문인지 본다.
#   인자: 로그 시작HH:MM:SS 끝HH:MM:SS 날짜(YYYY-MM-DD) [로그2 시작2 끝2 날짜2 …] — 묶음마다 표 하나. 출력: 표준 출력.
import sys, datetime, collections
KST = datetime.timezone(datetime.timedelta(hours=9))
def ep(d, hms): return datetime.datetime.fromisoformat(f'{d}T{hms}').replace(tzinfo=KST).timestamp()
a = sys.argv[1:]
for k in range(0, len(a), 4):
    f, s, e, d = a[k:k + 4]; t0, t1 = ep(d, s), ep(d, e)
    first, last, allf, alll = {}, {}, None, None
    for ln in open(f, encoding='utf-8', errors='replace'):
        p = ln.split()
        if len(p) < 3: continue
        try: t = int(p[0])
        except ValueError: continue
        if t < t0 or t > t1: continue
        if p[1] == 'ALL':
            v = list(map(int, p[3:]))
            if allf is None: allf = (t, v)
            alll = (t, v); continue
        key = (p[1], p[3] if len(p) > 3 else '?'); tk = int(p[2])
        first.setdefault(key, (t, tk)); last[key] = (t, tk)
    dt = alll[0] - allf[0]
    agg = collections.Counter()
    for key, (ta, ka) in first.items():
        tb, kb = last[key]
        if tb > ta: agg[key[1].strip('()')] += (kb - ka) / dt   # 틱 100 Hz → 초당 틱 = %
    dv = [y - x for x, y in zip(allf[1], alll[1])]; busy = sum(dv) - dv[3] - dv[4]
    print(f'== {f.split("/")[-1]} {s}~{e} ({dt} s) · 전체 {100 * busy / sum(dv):.1f} %(6 코어 평균)')
    for n, c in agg.most_common(14): print(f'  {n:24s} {c:6.1f} %')
