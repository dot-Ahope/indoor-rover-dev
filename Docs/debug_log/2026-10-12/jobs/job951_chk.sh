#!/bin/bash
# 10-12 §1: prep 뒤 확인(로버 안 움직임) — Nav2 수명 주기, 실행 중 PreferForward 가중, 원점, nvblox
for n in controller_server planner_server bt_navigator; do for i in 1 2 3; do r=$(timeout 15 ros2 lifecycle get /$n 2>&1 | tail -1); echo "$r" | grep -q "\[" && break; done; echo "  $n: $r"; done
for i in 1 2 3; do r=$(timeout 15 ros2 param get /controller_server FollowPathMPPI.PreferForwardCritic.cost_weight 2>&1 | tail -1); echo "$r" | grep -q value && break; done; echo "  실행 중 PreferForward: $r"
for i in 1 2 3; do r=$(timeout 15 ros2 param get /controller_server FollowPathMPPI.vx_min 2>&1 | tail -1); echo "$r" | grep -q value && break; done; echo "  vx_min: $r"
echo "  map→base: $(timeout 10 ros2 run tf2_ros tf2_echo map base_link 2>&1 | grep -a -m1 Translation)"
echo "  nvblox 컨테이너 노드: $(docker exec isaac_ros_dev-aarch64-container bash -c "pgrep -fc '^/opt/ros/humble/lib/nvblox_ros/nvblox_node' || true" 2>/dev/null)"
