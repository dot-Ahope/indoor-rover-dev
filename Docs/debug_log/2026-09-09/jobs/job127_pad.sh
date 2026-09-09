#!/bin/bash
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
sed -i 's/\r$//' /tmp/nav2_params.yaml
cp /tmp/nav2_params.yaml ~/ros2_ws/src/rover_navigation/config/
cp /tmp/nav2_params.yaml ~/ros2_ws/install/rover_navigation/share/rover_navigation/config/
echo "배포: $(grep -c 'footprint_padding: 0.05' ~/ros2_ws/install/rover_navigation/share/rover_navigation/config/nav2_params.yaml)곳"
for p in "navigation_launch" "controller_server" "planner_server" "bt_navigator" "behavior_server" "velocity_smoother" "smoother_server" "waypoint_follower" "lifecycle_manager_navigation" "stuck_monitor"; do pkill -9 -f "$p" 2>/dev/null; done
sleep 4
setsid nohup ros2 launch rover_navigation navigation.launch.py > /tmp/nav2.log 2>&1 &
sleep 28
for nd in /controller_server /planner_server /bt_navigator /behavior_server; do
  printf "  %-20s " "$nd"; timeout 6 ros2 lifecycle get "$nd" 2>/dev/null || echo "?"
done
echo "  오류: $(grep -aiE 'error|died' /tmp/nav2.log | tail -2 | cut -c1-120 | tr '\n' ' ')"
