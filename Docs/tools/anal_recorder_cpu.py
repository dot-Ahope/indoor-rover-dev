#!/usr/bin/env python3
"""anal_recorder_cpu — 주행별 bag 기록기(ros2 bag record)의 CPU 사용을 시간순으로, 다른 주요 프로세스·전체 부하와 함께 본다. (2026-10-13)
  왜: PreferForward 5 와 15 의 발행량은 같았다(anal_bag_rates). 남은 후보 = 받는 쪽(기록기)의 처리 속도 → 포화 전 구간에서 기록기 CPU·전체 여유가 다른지.
  입력: 러너가 남긴 proc_<이름>.log (2 s 마다 '시각 pid 누적틱 (이름)' + '시각 ALL cpu ...'). 틱 100 개 = 1 CPU·초, 코어 1 개 = 100 %.
  기록기 찾기: 이름이 ros2 인 프로세스 중 로그 구간에서 틱이 가장 많이 늘어난 것(launch 용 ros2 는 거의 0).
  사용: anal_recorder_cpu.py [--bin 10] 이름=proc.log ..."""
import sys, time, collections
BIN = 10; args = sys.argv[1:]
if args[0] == '--bin': BIN = int(args[1]); args = args[2:]
WATCH = ['controller_serv', 'ekf_node', 'localization_sl', 'nvblox_node', 'planner_server', 'bt_navigator']
for a in args:
    nm, f = a.split('=', 1); tick = collections.defaultdict(dict); comm = {}; tot = {}
    for l in open(f, errors='replace'):
        p = l.split()
        if len(p) < 4 or not p[0].isdigit(): continue
        t = int(p[0])
        if p[1] == 'ALL': v = [int(x) for x in p[3:11]]; tot[t] = (sum(v), v[3] + v[4]); continue   # 전체 틱, 유휴(idle+iowait)
        try: tick[p[1]][t] = int(p[2]); comm[p[1]] = p[3].strip('()')
        except ValueError: pass
    ts = sorted(tot); t0 = ts[0]
    def inc(pid, a_, b_):
        d = tick.get(pid, {}); ks = [k for k in d if a_ <= k <= b_]
        return (d[max(ks)] - d[min(ks)]) / max(max(ks) - min(ks), 1) if len(ks) > 1 else 0.0
    ros2 = [p for p in comm if comm[p] == 'ros2']; rec = max(ros2, key=lambda p: inc(p, ts[0], ts[-1]))
    byname = collections.defaultdict(list)
    for p, c in comm.items(): byname[c].append(p)
    print('== %s  %s~%s (%d s) · 기록기 pid %s' % (nm, time.strftime('%H:%M:%S', time.localtime(ts[0])), time.strftime('%H:%M:%S', time.localtime(ts[-1])), ts[-1] - ts[0], rec))
    print('  시각(+s)   기록기  전체 사용률      ' + '  '.join('%-9s' % w[:9] for w in WATCH))
    for b in range(0, ts[-1] - t0, BIN):
        A, B = t0 + b, t0 + b + BIN; ks = [k for k in ts if A <= k <= B]
        if len(ks) < 2: continue
        dt = tot[ks[-1]][0] - tot[ks[0]][0]; busy = 100.0 * (1 - (tot[ks[-1]][1] - tot[ks[0]][1]) / max(dt, 1))
        ncpu = round(dt / max(ks[-1] - ks[0], 1) / 100)
        print('  %s +%3d  %6.1f   %6.0f %% (코어 %d 개)   ' % (time.strftime('%H:%M:%S', time.localtime(A)), b, inc(rec, A, B), busy, ncpu) + '  '.join('%-9.1f' % sum(inc(p, A, B) for p in byname[w]) for w in WATCH))
