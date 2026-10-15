#!/bin/bash
# (10-14 10-15 §3) f2v1 뒤: 스무딩 실패 시각, 목표 시작/끝, 복구 동작, pad_relief 기록 — 로버 안 움직임
A=$(date -d '10:13:17' +%s)
grep -a -o '\[[a-z_0-9.-]*\] \[[A-Z]*\] \[[0-9]*\.[0-9]*\] \[[a-z_0-9.]*\]: .*' /tmp/nav2.log | awk -v a=$A '{t=$3; gsub(/[\[\]]/,"",t); if (t+0>=a) {printf "%s.%d %s %s\n", strftime("%H:%M:%S", t), (t-int(t))*10, $4, substr($0, index($0,$5), 110)}}' | grep -a "Begin navigating\|Goal succeeded\|Goal canceled\|Goal failed\|Smoothed path leads\|fail to compute\|Failed to make\|Running backup\|backup failed\|Running wait\|wait completed\|canceled. Stopping\|clear except" | uniq -c -f2 > /tmp/f2v1_events.txt; cat /tmp/f2v1_events.txt | cut -c1-170
echo "--- pad_relief"; cut -d' ' -f2- /tmp/pad_relief.log
