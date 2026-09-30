#!/bin/bash
# 09-30: Nav2 inactive 원인 확인
grep -aiE "error|fail|exception|footprint|invalid" /tmp/nav2.log | grep -av "^$" | head -15 | cut -c1-230
echo ---; for nd in /controller_server /planner_server /bt_navigator /local_costmap/local_costmap; do echo "$nd $(timeout 8 ros2 lifecycle get $nd 2>&1 | tail -1)"; done
