#!/bin/bash
S() { echo "$SPW" | sudo -S -p '' "$@"; }
S true
echo "== mon.log"; S tail -n 8 /var/log/wifi_mon/mon.log | cut -c1-230
echo "== wifi_mon 프로세스 트리"; P=$(systemctl show -p MainPID --value wifi-mon); echo "MainPID $P"; ps -o pid,ppid,stat,etime,wchan:20,args --ppid $P 2>/dev/null; ps -o pid,stat,etime,args -p $P
for c in $(pgrep -P $P); do echo "  자식 $c: $(ps -o args= -p $c)"; pgrep -P $c | while read g; do echo "    손자 $g: $(ps -o stat=,etime=,args= -p $g)"; done; done
echo "== iw 단독 시간"; t0=$(date +%s%N); S timeout 10 iw dev wlP1p1s0 scan freq 5180 >/dev/null 2>&1; echo "rc=$? $(( ($(date +%s%N)-t0)/1000000 )) ms"
