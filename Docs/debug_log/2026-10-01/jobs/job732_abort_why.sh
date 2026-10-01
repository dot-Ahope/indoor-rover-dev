#!/bin/bash
# 10-01 §8.2: f2a1 목표 1 ABORTED(36 s, map (0.55, 0.12)) — 원인 로그(읽기만). 11:05:30~11:06:30 구간.
python3 - "$@" <<'PY'
import re, datetime, sys
t0 = datetime.datetime.now().replace(hour=int(sys.argv[1]), minute=int(sys.argv[2]), second=int(sys.argv[3]), microsecond=0).timestamp(); t1 = t0 + int(sys.argv[4])
for f, pat in (('/tmp/nav2.log', r'warn|error|fail|abort|stuck|guard|collision|no valid|invalid|cancel|goal'), ('/tmp/slam.log', r'warn|error|fail')):
    print('--', f); seen = set()
    for l in open(f, errors='replace'):
        m = re.search(r'\[(\d{10})\.\d+\]', l)
        if not m or not (t0 <= int(m.group(1)) <= t1) or not re.search(pat, l, re.I) or 'Message Filter' in l: continue
        k = re.sub(r'\[\d{10}\.\d+\]', '', l).strip()[:220]
        if k in seen: continue
        seen.add(k); print('%s %s' % (datetime.datetime.fromtimestamp(int(m.group(1))).strftime('%H:%M:%S'), k))
PY
