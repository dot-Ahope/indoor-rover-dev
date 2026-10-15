#!/bin/bash
# (10-15 §29.2) 제어 주기 놓침 경고의 10 s 단위 분포 + 목표 시작/끝 시각 — 로버 안 움직임
L=/tmp/nav2.log
grep -a "Control loop missed" $L | grep -o "\[17[0-9]*\.[0-9]*\]" | tr -d '[]' | awk '{b=int($1/10)*10; c[b]++} END {for (k in c) print k, c[k]}' | sort -n | while read t n; do echo "$(date -d @$t +%H:%M:%S) $n"; done
grep -a "Begin navigating\|Goal succeeded\|Received goal" $L | grep -o "\[17[0-9]*\.[0-9]*\].*" | cut -c1-120 | while read l; do t=$(echo $l | cut -d']' -f1 | tr -d '['); echo "$(date -d @${t%.*} +%H:%M:%S) ${l#*]}"; done | tail -8
ls -la /tmp/logkeep 2>/dev/null | tail -5
