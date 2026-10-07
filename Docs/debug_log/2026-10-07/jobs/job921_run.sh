#!/bin/bash
# 10-07 §7: f2d2 목표 10(출발 복귀) 상자 앞 정지 — nav2 로그 + bag 추출(읽기만, 1~2 분)
python3 - <<'PY'
import re, datetime
pat = re.compile(r'PathBlocked|nav_guard|[Ff]ail|[Aa]bort|[Cc]ancel|[Rr]ecovery|clear|[Bb]ack[Uu]p|Wait|wait|collision|Optimizer|[Ss]tuck|extrapolation|Begin navigating|Reached')
for L in open('/tmp/nav2.log', errors='replace'):
    m = re.search(r'\[(\d{10})\.(\d+)\]', L)
    if not m or not (1791346600 <= int(m.group(1)) <= 1791346730) or 'Message Filter' in L or not pat.search(L): continue
    print('%+6.1f' % (int(m.group(1)) - 1791346297), re.sub(r'^\[[a-z_.]+-\d+\] ', '', L.strip())[:200])
PY
python3 /tmp/job912_extract.py /tmp/bag_f2d2 1791346590 1791346730 /tmp/x921_f2d2.npz 2>&1 | grep -v rosbag2_storage
