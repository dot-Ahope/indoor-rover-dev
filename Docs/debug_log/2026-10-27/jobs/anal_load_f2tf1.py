#!/usr/bin/env python3
"""anal_load_f2tf1 — §21 부하(§16 ③) 원인: 주행 중 CPU 포화 정도 · 프로세스별 몫 · TF 지연 순간과의 관계 (2026-10-27, PC).
  입력: 러너 proc 기록(2 s 간격 /proc/<pid>/stat utime+stime 틱 · ALL = /proc/stat cpu 줄), tegrastats(1 s, 코어별 % · 주파수),
        nav2.log(층 경고 · Control loop missed · 컨트롤러 TF 외삽 중단), 1 s top(-c, 명령줄로 프로세스 이름).
  인자: proc.log tegra.log nav2.log top1s.txt 주행시작HH:MM:SS 주행끝HH:MM:SS"""
import sys, re, time, collections
import numpy as np
day = '2026-10-27 '
T0 = time.mktime(time.strptime(day + sys.argv[5], '%Y-%m-%d %H:%M:%S')); T1 = time.mktime(time.strptime(day + sys.argv[6], '%Y-%m-%d %H:%M:%S'))
HZ = 100.0; NC = 6
# 1) 프로세스 이름: top -c 명령줄에서 (pid → 짧은 이름)
name = {}
for l in open(sys.argv[4], encoding='utf-8', errors='replace'):
    m = re.match(r'\s*(\d+)\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+\S\s+[\d.]+\s+[\d.]+\s+\S+\s+(.*)', l)
    if not m: continue
    cmd = m[2]; nm = re.search(r'__node:=(\w+)', cmd)
    base = cmd.split()[0].split('/')[-1]
    if base.startswith('python'): base = cmd.split()[1].split('/')[-1] if len(cmd.split()) > 1 else base
    name[m[1]] = (nm[1] + '(' + base + ')') if nm else base
# 2) proc 기록
S = collections.defaultdict(dict); ALL = {}
for l in open(sys.argv[1], encoding='utf-8', errors='replace'):
    p = l.split()
    if len(p) < 3: continue
    if not p[0].isdigit(): continue
    t = int(p[0])
    if p[1] == 'ALL': ALL[t] = list(map(int, p[3:10])); continue
    try: S[t][p[1]] = (int(p[2]), ' '.join(p[3:]).strip('()'))
    except ValueError: pass
ts = sorted(t for t in S if T0 - 2 <= t <= T1 + 2)
tot = collections.Counter(); dur = ts[-1] - ts[0]
for a, b in zip(ts, ts[1:]):
    for pid, (j, cm) in S[b].items():
        if pid in S[a]: tot[pid] += max(j - S[a][pid][0], 0)
allb = [ALL[t] for t in ts if t in ALL]; d = np.array(allb[-1]) - np.array(allb[0]); busy = 1 - (d[3] + d[4]) / d.sum()
print('주행 %s~%s (%d s) · 전체 CPU 사용률(/proc/stat) %.1f %% (%d 코어 기준, 100 %% = 모든 코어 포화)' % (sys.argv[5], sys.argv[6], dur, 100 * busy, NC))
print('프로세스별 평균 CPU(코어 1 개 = 100 %%), 상위 15:')
for pid, j in tot.most_common(15):
    cm = S[ts[-1]].get(pid, S[ts[0]].get(pid, (0, '?')))[1]
    print('  %6.1f %%  %-8s %s' % (100 * j / HZ / dur, pid, name.get(pid, cm)))
sumtop = sum(tot.values()) / HZ / dur; print('  (프로세스 합 %.0f %% = 코어 %.2f 개분, 전체 용량 %d 개)' % (100 * sumtop, sumtop, NC))
# 3) tegrastats 코어 % · 주파수
TG = []
for l in open(sys.argv[2], encoding='utf-8', errors='replace'):
    m = re.match(r'(\d\d-\d\d-\d{4} \d\d:\d\d:\d\d).*?CPU \[([^\]]+)\]', l)
    if not m: continue
    t = time.mktime(time.strptime(m[1], '%m-%d-%Y %H:%M:%S'))
    if not T0 <= t <= T1: continue
    c = [(int(a), int(f)) for a, f in re.findall(r'(\d+)%@(\d+)', m[2])]
    TG.append((t, np.mean([x[0] for x in c]), min(x[0] for x in c), max(x[1] for x in c)))
TA = np.array(TG); print('tegrastats %d 초: 코어 평균 %% 중앙 %.0f · 10%% %.0f · 90%% %.0f · 최소 코어 %% 중앙 %.0f · 주파수 %d MHz(최대)' % (
    len(TA), np.median(TA[:, 1]), np.percentile(TA[:, 1], 10), np.percentile(TA[:, 1], 90), np.median(TA[:, 2]), TA[:, 3].max()))
print('  코어 평균 ≥ 95 %% 인 초 비율 %.0f %%' % (100 * np.mean(TA[:, 1] >= 95)))
# 4) 사건과 tegrastats
EV = collections.defaultdict(list)
for l in open(sys.argv[3], encoding='utf-8', errors='replace'):
    m = re.search(r'\[(\d{10}\.\d+)\]', l)
    if not m: continue
    t = float(m[1])
    if not T0 <= t <= T1: continue
    if 'NvbloxCostmapLayer' in l and "Can't transform" in l: EV['층 경고'].append(t)
    elif 'Control loop missed' in l: EV['Control loop missed'].append(t)
    elif 'extrapolation into the future' in l and 'controller_server' in l and 'transformPose' in l: EV['컨트롤러 TF 중단'].append(t)
tg_t = TA[:, 0]
for k, L in EV.items():
    v = [TA[np.argmin(np.abs(tg_t - int(t))), 1] for t in L]
    print('%s %d 번 · 그 초 코어 평균 %% 중앙 %.0f (전체 중앙 %.0f)' % (k, len(L), np.median(v) if v else -1, np.median(TA[:, 1])))
