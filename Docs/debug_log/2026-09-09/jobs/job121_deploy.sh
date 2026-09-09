#!/bin/bash
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
cp /tmp/nav2_params.yaml ~/ros2_ws/src/rover_navigation/config/
cp /tmp/nav2_params.yaml ~/ros2_ws/install/rover_navigation/share/rover_navigation/config/
cp /tmp/stuck_monitor.py ~/ros2_ws/src/rover_bringup/scripts/
cp /tmp/stuck_monitor.py ~/ros2_ws/install/rover_bringup/lib/rover_bringup/ 2>/dev/null
chmod +x ~/ros2_ws/src/rover_bringup/scripts/stuck_monitor.py ~/ros2_ws/install/rover_bringup/lib/rover_bringup/stuck_monitor.py 2>/dev/null
echo "배포 확인:"
grep -nE "^      (lookahead_dist|min_lookahead_dist):" ~/ros2_ws/install/rover_navigation/share/rover_navigation/config/nav2_params.yaml | sed 's/^/  /'
grep -nE "recovery_until|cb_behavior" ~/ros2_ws/install/rover_bringup/lib/rover_bringup/stuck_monitor.py | head -4 | sed 's/^/  /'
echo ""
echo "=== Nav2 재기동 ==="
for p in "navigation_launch" "controller_server" "planner_server" "bt_navigator" "behavior_server" "velocity_smoother" "smoother_server" "waypoint_follower" "lifecycle_manager_navigation" "stuck_monitor"; do pkill -9 -f "$p" 2>/dev/null; done
sleep 4
setsid nohup ros2 launch rover_navigation navigation.launch.py > /tmp/nav2.log 2>&1 &
sleep 26
for nd in /controller_server /planner_server /bt_navigator /behavior_server /velocity_smoother; do
  printf "  %-22s " "$nd"; timeout 6 ros2 lifecycle get "$nd" 2>/dev/null || echo "?"
done
echo "  stuck_monitor: $(ros2 node list 2>/dev/null | grep -a stuck_monitor || echo 없음)"
grep -a "stuck_monitor 시작" /tmp/nav2.log | tail -1 | sed 's/^/  /'
echo "  nav2 오류: $(grep -aiE 'error|exception' /tmp/nav2.log | tail -2 | tr '\n' ' ')"
