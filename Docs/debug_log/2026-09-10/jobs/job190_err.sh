#!/bin/bash
echo "=== lifecycle 오류 전문 ==="
grep -aiE "Failed to change state|Exception|Timed out|planner_server" /tmp/nav2.log | tail -8
echo ""
echo "=== planner_server 관련 전체 ==="
grep -a "planner_server" /tmp/nav2.log | tail -10 | cut -c1-200
