#!/bin/bash
# (10-14 §17) 주행 중 실시간 확인: 최근 60 s Nav2 경고·오류, pad_relief 기록 — 로버에 명령 안 보냄(DDS 참여자도 안 만듦)
A=$(( $(date +%s) - 60 ))
grep -a -o '\[[a-z_0-9.-]*\] \[[A-Z]*\] \[[0-9]*\.[0-9]*\] \[[a-z_0-9.]*\]: .*' /tmp/nav2.log | awk -v a=$A '{t=$3; gsub(/[\[\]]/,"",t); if (t+0>=a) {printf "%s %s %s %s\n", strftime("%H:%M:%S", t), $2, $4, substr($0, index($0,$5), 120)}}' | grep -av "Received a path\|Passing new path" | uniq -c -f2 | tail -25
echo "--- pad_relief"; cut -d' ' -f2- /tmp/pad_relief.log | tail -4; date +%T
