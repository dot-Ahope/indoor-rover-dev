#!/bin/bash
# (10-14 §13.1) f2s1 목표 3 취소 전후 Nav2·nav_guard 로그 — 로버 안 움직임
A=$(date -d '13:47:13' +%s); B=$(date -d '13:48:40' +%s)
grep -a -o '\[[a-z_0-9.-]*\] \[[A-Z]*\] \[[0-9]*\.[0-9]*\] \[[a-z_0-9.]*\]: .*' /tmp/nav2.log | awk -v a=$A -v b=$B '{t=$3; gsub(/[\[\]]/,"",t); if (t+0>=a && t+0<=b) {printf "%s.%d %s %s %s\n", strftime("%H:%M:%S", t), (t-int(t))*10, $2, $4, substr($0, index($0,$5), 140)}}' | grep -av "Received a path to smooth\|Passing new path\|missed its desired rate" | uniq -c -f3 | head -60
echo "--- nav_guard / 정체 감시"; grep -a "nav_guard\|stuck_monitor\|STUCK\|guard" /tmp/nav2.log | grep -a "$(date -d '13:4' +%H:%M)\|STUCK\|취소\|한도" | tail -8 | cut -c1-200
