#!/bin/bash
# (10-15 §32) 17:36:00~17:37:20 초별 제어 주기 놓침 수 + 이벤트(재계획 · 취소 · 탈출 · 크리틱 시간) — 로버 안 움직임
L=/tmp/nav2.log; A=$(date -d "today 17:36:00" +%s); B=$(date -d "today 17:37:20" +%s)
grep -a "Control loop missed" $L | grep -o "\[17[0-9]*\.[0-9]*\]" | tr -d '[]' | awk -v a=$A -v b=$B '$1>=a && $1<b {c[int($1)]++} END {for (k in c) print k, c[k]}' | sort -n | while read t n; do echo "놓침 $(date -d @$t +%H:%M:%S) $n"; done
grep -a "PathBlockedAhead\|canceled\|Running monotone\|ClearanceBandCritic 시간\|Begin navigating\|Goal succeeded\|fail to compute\|Smoothed path leads" $L | grep -v "지속되면" | while read l; do t=$(echo "$l" | grep -o "\[17[0-9]*\.[0-9]*\]" | head -1 | tr -d '[]'); [ -n "$t" ] && [ ${t%.*} -ge $A ] && [ ${t%.*} -lt $B ] && echo "사건 $(date -d @${t%.*} +%H:%M:%S) ${l#*]: }" | cut -c1-170; done
