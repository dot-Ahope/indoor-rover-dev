#!/bin/bash
# 10-01 §8.28: MPPI vx_min 0 배포 → Nav2 만 재시작(위치 추정 유지)
cp /tmp/f14/nav2_params.yaml ~/ros2_ws/src/rover_navigation/config/ && cd ~/ros2_ws && colcon build --packages-select rover_navigation 2>&1 | tail -1
bash /tmp/job760_nav2_restart.sh
echo "  MPPI vx_min: $(timeout 10 ros2 param get /controller_server FollowPathMPPI.vx_min 2>&1 | tail -1) | 전역: $(timeout 10 ros2 param get /global_costmap/global_costmap plugins 2>&1 | tail -1)"
