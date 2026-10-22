#!/bin/bash
# 10-22 §6 f2dr1 목표 1 ABORTED(29 s) — 13:50:20~13:51:00 nav2 사건(시각 KST) + 로그 원본을 ~/bags/logs_f2dr1 로 보관
mkdir -p ~/bags/logs_f2dr1; cp /tmp/nav2.log /tmp/slam.log /tmp/sensors.log ~/bags/logs_f2dr1/ 2>/dev/null; ls -la ~/bags/logs_f2dr1 | tail -3
A=$(date -d "13:50:20" +%s); B=$(date -d "13:51:00" +%s)
awk -v a=$A -v b=$B 'match($0,/\[1[0-9]{9}\.[0-9]+\]/){t=substr($0,RSTART+1,RLENGTH-2)+0; if(t>=a&&t<=b) print}' /tmp/nav2.log \
 | grep -aiE "abort|fail|collision|block|recover|extrapol|wait|backup|spin|clear|stuck|escape|goal|no valid|invalid|cancel" \
 | grep -av "get_state\|Failed to get parameters" \
 | awk 'match($0,/\[1[0-9]{9}\.[0-9]+\]/){t=substr($0,RSTART+1,RLENGTH-2); cmd="date -d @"t" +%H:%M:%S.%2N"; cmd|getline s; close(cmd); print s" "substr($0,1,200)}' | head -60
