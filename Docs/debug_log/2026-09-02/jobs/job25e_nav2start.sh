#!/bin/bash
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
pkill -f "navigation_launch|controller_server|planner_server|bt_navigator|behavior_server|velocity_smoother|smoother_server|waypoint_follower|lifecycle_manager_navigation" 2>/dev/null
sleep 3
setsid nohup ros2 launch rover_navigation navigation.launch.py > /tmp/nav2.log 2>&1 &
sleep 25
echo "=== lifecycle ==="
for nd in /controller_server /planner_server /bt_navigator /behavior_server /velocity_smoother; do
  printf "  %-20s " "$nd"; timeout 6 ros2 lifecycle get "$nd" 2>/dev/null || echo "미기동"
done
echo "=== progress_checker ==="
timeout 8 ros2 param get /controller_server progress_checker.plugin 2>/dev/null || echo "  조회실패"
timeout 8 ros2 param get /controller_server progress_checker.required_movement_angle 2>/dev/null || true
echo "=== 기동 오류 ==="
grep -aiE "error|exception|fail" /tmp/nav2.log | grep -avi "0 errors" | tail -5 || echo "  없음"
echo "  load: $(cat /proc/loadavg | cut -d' ' -f1-3)"
