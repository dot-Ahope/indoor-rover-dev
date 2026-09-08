#!/bin/bash
# Nav2 만 강제 종료 (센서·slam·agent 유지). ssh 인라인 금지 — 파일로 실행할 것.
source /opt/ros/humble/setup.bash
pkill -f "ros2 launch rover_navigation"
for p in controller_server planner_server bt_navigator behavior_server velocity_smoother smoother_server waypoint_follower lifecycle_manager_navigation stuck_monitor; do
  pkill -9 -f "$p"
done
sleep 3
echo -n "Nav2 잔존: "; pgrep -f "controller_server|planner_server|bt_navigator|behavior_server|velocity_smoother|stuck_monitor" | wc -l
source ~/ros2_ws/install/setup.bash
echo -n "남은 노드: "; ros2 node list 2>/dev/null | grep -vE "transform_listener" | tr "\n" " "; echo
echo -n "보드 상태: "; timeout 6 ros2 topic echo --once /rover/status 2>/dev/null | grep message | head -1
echo -n "cmd_vel 발행자: "; ros2 topic info /cmd_vel 2>/dev/null | grep -a "Publisher count"
