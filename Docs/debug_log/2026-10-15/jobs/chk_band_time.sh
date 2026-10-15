#!/bin/bash
# (10-15 §29.6) 크리틱 계산 시간 기록 · 놓침 수 — 로버 안 움직임
grep -a "ClearanceBandCritic 시간" /tmp/nav2.log | sed 's/.*시간: //' | awk '{print}' | tail -60 | awk '{a=$2; m=$6; print a, m}' | sort -k2 -n | tail -5
echo "기록 수 $(grep -ac 'ClearanceBandCritic 시간' /tmp/nav2.log) · 평균 ms 중앙값 $(grep -a 'ClearanceBandCritic 시간' /tmp/nav2.log | sed 's/.*평균 //' | awk '{print $1}' | sort -n | awk '{a[NR]=$1} END {print a[int(NR/2)+1]}') · 최대 ms 최대 $(grep -a 'ClearanceBandCritic 시간' /tmp/nav2.log | sed 's/.*최대 //' | awk '{print $1}' | sort -n | tail -1)"
echo "제어 주기 놓침: $(grep -ac 'Control loop missed' /tmp/nav2.log) · Optimizer fail: $(grep -ac 'fail to compute path' /tmp/nav2.log) · 탈출 $(grep -ac 'Running monotone_escape' /tmp/nav2.log)"
