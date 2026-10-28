#!/bin/bash
# §13 dry_run 에서 경로 조회가 전부 '경로 없음(상태 6)' — 계획기 상태 확인(로버 안 움직임)
date +%T; uptime
tail -c 300000 /tmp/nav2.log | grep -a "planner_server\|smac\|Smac\|NavFn\|ERROR\|Failed\|failed" | tail -25 | cut -c1-230
echo == procs; pgrep -fa "planner_server|controller_server|bt_navigator|slam|nvblox" | cut -c1-120
