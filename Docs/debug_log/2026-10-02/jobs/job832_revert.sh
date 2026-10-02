#!/bin/bash
# 10-02 §12.1: A/B 끝 — Nav2 를 기본(local_frame odom)으로 재시작
source ~/ros2_ws/install/setup.bash
NAV_EXTRA="" bash /tmp/job760_nav2_restart.sh 2>&1 | tail -4
echo "  local global_frame: $(timeout 15 ros2 param get /local_costmap/local_costmap global_frame 2>&1 | tail -1)"
