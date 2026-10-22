#!/bin/bash
# 10-22 §5.3 prep 3 회째 PREP_FAIL — 기다림 끝 이유 · nav2 기동 오류
grep -av "기다리는 것" /tmp/prepchk.txt | tail -12
echo "--- nav2.log 오류"; grep -aiE "error|fatal|died|exception|failed" /tmp/nav2.log | cut -c1-220 | head -20
echo "--- nav2 노드 수"; pgrep -fa "controller_server|planner_server|bt_navigator|behavior_server" | cut -c1-120
