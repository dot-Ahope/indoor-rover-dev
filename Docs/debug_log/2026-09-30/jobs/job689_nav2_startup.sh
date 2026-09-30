#!/bin/bash
# 09-30: Nav2 lifecycle 재기동(STARTUP) — 첫 기동이 behavior_server get_state 실패로 중단됨
timeout 90 ros2 service call /lifecycle_manager_navigation/manage_nodes nav2_msgs/srv/ManageLifecycleNodes "{command: 0}" 2>&1 | tail -1
for nd in /controller_server /planner_server /bt_navigator /behavior_server; do echo "$nd $(timeout 8 ros2 lifecycle get $nd 2>&1 | tail -1)"; done
