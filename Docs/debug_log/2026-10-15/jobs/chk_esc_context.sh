#!/bin/bash
# (10-15 §29.6) 탈출 실행 전후 nav2.log 문맥 — 로버 안 움직임
L=/tmp/nav2.log; n=$(grep -an "Running monotone_escape" $L | head -1 | cut -d: -f1); [ -z "$n" ] && { echo 없음; exit; }
sed -n "$((n-40)),$((n+12))p" $L | grep -av "Control loop missed\|ClearanceBandCritic 시간" | cut -c1-230 | while read l; do t=$(echo "$l" | grep -o "\[17[0-9]*\.[0-9]*\]" | head -1 | tr -d '[]'); [ -n "$t" ] && echo "$(date -d @${t%.*} +%H:%M:%S) ${l#*]: }" || echo "$l"; done | tail -30
