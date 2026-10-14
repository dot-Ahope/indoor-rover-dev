#!/bin/bash
# (10-14 §9.2) f2r1 상자 옆 11:26:34~11:26:50 의 Nav2 로그 원문 — 로버 안 움직임
A=$(date -d '11:26:34' +%s); B=$(date -d '11:26:50' +%s)
grep -a -o '\[[a-z_0-9.-]*\] \[[A-Z]*\] \[[0-9]*\.[0-9]*\] \[[a-z_0-9.]*\]: .*' /tmp/nav2.log | awk -v a=$A -v b=$B '{t=$3; gsub(/[\[\]]/,"",t); if (t+0>=a && t+0<=b) {printf "%s.%02d %s %s %s\n", strftime("%H:%M:%S", t), (t-int(t))*100, $2, $4, substr($0, index($0,$5), 150)}}' | head -60
