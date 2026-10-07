#!/bin/bash
# 10-07 §2: f2c1 목표 4(남서) 취소 원인 — nav2 로그(11:00:30 이후, 읽기만)
python3 - <<'PY'
import re, datetime
s = datetime.datetime(2026, 10, 7, 11, 0, 30).timestamp()
pat = re.compile(r'PathBlocked|nav_guard|[Ff]ail|[Aa]bort|[Cc]ancel|Received|[Rr]ecovery|clear|[Bb]ack[Uu]p|Wait|[Gg]oal|collision|Optimizer|[Ss]tuck')
for L in open('/tmp/nav2.log', errors='replace'):
    m = re.search(r'\[(\d{10})\.(\d+)\]', L)
    if not m or int(m.group(1)) < s or 'Message Filter' in L or not pat.search(L): continue
    t = datetime.datetime.fromtimestamp(int(m.group(1))).strftime('%H:%M:%S')
    print(t, re.sub(r'^\[[a-z_]+-\d+\] ', '', L.strip())[:190])
PY
grep -a "nav_guard\|stuck" /tmp/f0_f2c1.log | tail -5; ls -t /tmp/*.log | head -12 | tr "\n" " "
