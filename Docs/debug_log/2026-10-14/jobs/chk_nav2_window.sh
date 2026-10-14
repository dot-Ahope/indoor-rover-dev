#!/bin/bash
# (10-14 §24) Nav2 기록의 한 시각 구간을 거르지 않고 출력 — 로버 안 움직임. 인자: 시작HH:MM:SS 끝HH:MM:SS
A=$(date -d "$1" +%s); B=$(date -d "$2" +%s)
grep -a -o '\[[a-z_0-9.-]*\] \[[A-Z]*\] \[[0-9]*\.[0-9]*\] \[[a-z_0-9.]*\]: .*' /tmp/nav2.log | awk -v a=$A -v b=$B '{t=$3; gsub(/[\[\]]/,"",t); if (t+0>=a && t+0<=b) {printf "%s.%d %s %s\n", strftime("%H:%M:%S", t), (t-int(t))*10, $2, substr($0, index($0,$4), 150)}}'
