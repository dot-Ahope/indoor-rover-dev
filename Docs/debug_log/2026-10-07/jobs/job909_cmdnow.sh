#!/bin/bash
# 10-07: 지금 움찔댐 — /cmd_vel 발행자·현재 값·Nav2 활성 목표 확인(읽기만)
date +%T; ros2 topic info /cmd_vel -v 2>/dev/null | grep -aE "Node name|Publisher count" | head -8
timeout 4 ros2 topic echo /cmd_vel --once 2>&1 | head -8 | tr '\n' ' '; echo
timeout 5 ros2 topic hz /cmd_vel 2>&1 | grep -a average | tail -1
tail -8 /tmp/nav2.log | cut -c1-200
pgrep -fa "job550|job551|f0run|teleop" | grep -v pgrep | cut -c1-120
