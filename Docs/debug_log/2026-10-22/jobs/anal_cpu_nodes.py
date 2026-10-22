#!/usr/bin/env python3
"""anal_cpu_nodes — 러너 proc 로그(시각 · pid · 누적 CPU 틱 · (comm))로 주행 동안 프로세스별 평균 CPU %(한 코어 = 100 %) (2026-10-22 §18, PC).
  왜: 멈칫 A(TF 늦음) · B(제어 주기 늦음)의 배경이 CPU 바쁨인지 — 무엇이 CPU 를 쓰는지 먼저 나눈다.
  틱 = /proc/<pid>/stat utime+stime(CLK_TCK 100 가정). 같은 comm 은 합쳐 함께 보임. 컨테이너 안 프로세스도 호스트 pid 로 잡힘.
  인자: proc 로그 [상위 N=25]"""
import sys, re, collections
f = sys.argv[1]; N = int(sys.argv[2]) if len(sys.argv) > 2 else 25
first, lastv, name, ts = {}, {}, {}, []
for line in open(f, encoding='utf-8', errors='replace'):
    m = re.match(r'^(\d+) (\d+) (\d+) \((.*)\)\s*$', line.strip())
    if not m: continue
    t, pid, tk, comm = int(m[1]), int(m[2]), int(m[3]), m[4]
    ts.append(t)
    if pid not in first: first[pid] = (t, tk)
    lastv[pid] = (t, tk); name[pid] = comm
T0, T1 = min(ts), max(ts); dur = T1 - T0
rows = []
for pid in first:
    (ta, ka), (tb, kb) = first[pid], lastv[pid]
    if tb - ta < dur * 0.5: continue   # 주행 절반 넘게 살아 있던 것만
    rows.append((100.0 * (kb - ka) / 100.0 / (tb - ta), pid, name[pid]))
rows.sort(reverse=True); tot = sum(r[0] for r in rows)
print('proc 로그 %s · %d s · 프로세스 %d · 합 %.0f %%(6 코어 = 600 %%)' % (f.split('/')[-1], dur, len(rows), tot))
for c, pid, nm in rows[:N]: print('  %5.1f %%  pid %-8d %s' % (c, pid, nm))
g = collections.defaultdict(float)
for c, pid, nm in rows: g[nm] += c
print('같은 이름 합 상위:'); [print('  %5.1f %%  %s' % (v, k)) for k, v in sorted(g.items(), key=lambda q: -q[1])[:12]]
