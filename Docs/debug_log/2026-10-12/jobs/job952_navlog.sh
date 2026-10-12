#!/bin/bash
# 10-12 §2: f2f1 주행 중 Nav2·EKF·SLAM 로그의 경고·오류(10:32~10:36) — 로버 안 움직임
ls -la /tmp/*.log 2>/dev/null | awk '{print $5, $9}' | head -30
for f in /tmp/nav2.log /tmp/nav.log /tmp/navigation.log; do [ -f $f ] && { echo "== $f"; grep -aE "WARN|ERROR|extrapolat|Failed|failed|abort|Abort|timed out|exceed|missed|rate" $f | python3 -c "
import sys,re,time
for l in sys.stdin:
    m=re.search(r'\[(\d{10})\.(\d+)\]',l)
    if not m: continue
    t=int(m.group(1))
    if 1791768720<=t<=1791768980: print(time.strftime('%H:%M:%S',time.localtime(t)), re.sub(r'\[\d{10}\.\d+\] ','',l.strip())[:230])
" | awk '{k=$0; sub(/^[0-9:]+ /,"",k); if(k!=p){print; p=k}}' | head -80; }; done
