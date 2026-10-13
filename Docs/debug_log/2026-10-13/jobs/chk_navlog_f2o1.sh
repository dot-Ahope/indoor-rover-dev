#!/bin/bash
# (오늘만) f2o1 목표 3 중단 전후(13:33:05~13:33:50)의 Nav2 로그 원문 — 로버 안 움직임
A=$(date -d '13:33:05' +%s); B=$(date -d '13:33:50' +%s)
grep -a -o '\[[a-z_0-9.-]*\] \[[A-Z]*\] \[[0-9]*\.[0-9]*\] \[[a-z_0-9.]*\]: .*' /tmp/nav2.log | awk -v a=$A -v b=$B '{t=$3; gsub(/[\[\]]/,"",t); if (t+0>=a && t+0<=b) {printf "%s %s %s %s\n", strftime("%H:%M:%S", t), $2, $4, substr($0, index($0,$5), 170)}}' | uniq -c -f3 | head -70
echo "--- 로그 크기 $(wc -l < /tmp/nav2.log) 줄 · 13:30:16 이후 ERROR/WARN 종류"
S0=$(date -d '13:30:16' +%s); grep -a -o '\[\(ERROR\|WARN\)\] \[[0-9]*\.[0-9]*\] \[[a-z_0-9.]*\]: .\{0,60\}' /tmp/nav2.log | awk -v a=$S0 '{t=$2; gsub(/[\[\]]/,"",t); if (t+0>=a) {$2=""; print}}' | sed 's/[0-9.-]\{3,\}/N/g' | sort | uniq -c | sort -rn | head -20
cp /tmp/nav2.log /tmp/nav2_f2o1.log
