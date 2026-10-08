#!/bin/bash
# 10-08 §3: B 구성 확인(읽기만) — MPPI visualize·/trajectories 발행·Nav2 상태
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "MPPI visualize: $(timeout 10 ros2 param get /controller_server FollowPathMPPI.visualize 2>&1 | tail -1)"
for n in controller_server planner_server bt_navigator; do echo "$n: $(timeout 10 ros2 lifecycle get /$n 2>&1 | tail -1)"; done
ros2 topic list 2>/dev/null | grep -E "trajectories|transformed_global_plan"
