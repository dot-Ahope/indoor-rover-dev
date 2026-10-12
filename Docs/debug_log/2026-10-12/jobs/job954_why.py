# 10-12 §3.2: f2f2 목표 1 취소 원인 — 주행 창(11:16:35~11:17:35)의 Nav2·guard·stuck 로그. 로버 안 움직임
import re, time, glob, os
A, B = 1791771390, 1791771460
for f in sorted(glob.glob('/tmp/*.log')):
    if os.path.getsize(f) > 80e6 or 'bag_' in f or 'top_' in f or 'proc_' in f or 'tegra' in f or 'live' in f: continue
    out = []; last = None
    for l in open(f, errors='replace'):
        m = re.search(r'\[(\d{10})\.\d+\]', l)
        if not m or not (A <= int(m.group(1)) <= B): continue
        if not re.search(r'WARN|ERROR|cancel|Cancel|취소|guard|stuck|정체|Abort|abort|Received a goal|Goal|goal', l): continue
        k = re.sub(r'\d+\.\d+', '#', l)
        if k == last: continue
        last = k; out.append(time.strftime('%H:%M:%S', time.localtime(int(m.group(1)))) + ' ' + re.sub(r'\[\d{10}\.\d+\] ', '', l.strip())[:210])
    if out: print('== %s (%d 줄)' % (f, len(out))); print('\n'.join(out[:45]))
