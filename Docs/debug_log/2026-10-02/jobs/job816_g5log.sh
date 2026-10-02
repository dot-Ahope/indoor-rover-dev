#!/bin/bash
# 10-02 §6.4: f2b3 목표 5(전체 6) 정지·취소 원인 — nav2 로그(13:24:55 이후)
python3 - <<'PY'
import re, datetime
s = datetime.datetime(2026, 10, 2, 13, 24, 55).timestamp()
pat = re.compile(r'PathBlocked|nav_guard|[Ff]ail|[Aa]bort|[Cc]ancel|Received|[Rr]ecovery|clear|[Bb]ack[Uu]p|Wait|[Gg]oal|collision|Optimizer|[Ss]tuck')
for L in open('/tmp/nav2.log', errors='replace'):
    m = re.search(r'\[(\d{10})\.(\d+)\]', L)
    if not m or int(m.group(1)) < s or 'Message Filter' in L or not pat.search(L): continue
    t = datetime.datetime.fromtimestamp(int(m.group(1))).strftime('%H:%M:%S')
    print(t, re.sub(r'^\[[a-z_]+-\d+\] ', '', L.strip())[:190])
PY
