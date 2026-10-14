#!/bin/bash
# (10-14 §17) 주행 중: 목표 시작·성공·실패 시각(Nav2 로그), 최근 컨트롤러 실패 — 명령 없음
A=$(date -d '15:20:50' +%s)
grep -a -o '\[[a-z_0-9.-]*\] \[[A-Z]*\] \[[0-9]*\.[0-9]*\] \[[a-z_0-9.]*\]: .*' /tmp/nav2.log | awk -v a=$A '{t=$3; gsub(/[\[\]]/,"",t); if (t+0>=a) {printf "%s %s %s\n", strftime("%H:%M:%S", t), $4, substr($0, index($0,$5), 130)}}' | grep -a "Begin navigating\|Goal succeeded\|Goal failed\|canceled\|fail to compute\|Failed to make\|Collision\|backup\|nav_guard\|blocked\|Aborting handle" | grep -av "smooth_path" | tail -30
date +%T
