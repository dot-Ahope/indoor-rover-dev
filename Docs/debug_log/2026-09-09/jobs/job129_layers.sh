#!/bin/bash
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
sed -i 's/\r$//' /tmp/nav2_params.yaml
cp /tmp/nav2_params.yaml ~/ros2_ws/src/rover_navigation/config/
cp /tmp/nav2_params.yaml ~/ros2_ws/install/rover_navigation/share/rover_navigation/config/
echo "배포: obstacle_layer $(grep -c 'obstacle_layer:' ~/ros2_ws/install/rover_navigation/share/rover_navigation/config/nav2_params.yaml)곳, voxel 소스 depth $(grep -c 'observation_sources: depth' ~/ros2_ws/install/rover_navigation/share/rover_navigation/config/nav2_params.yaml)곳"
for p in "navigation_launch" "controller_server" "planner_server" "bt_navigator" "behavior_server" "velocity_smoother" "smoother_server" "waypoint_follower" "lifecycle_manager_navigation" "stuck_monitor"; do pkill -9 -f "$p" 2>/dev/null; done
sleep 4
setsid nohup ros2 launch rover_navigation navigation.launch.py > /tmp/nav2.log 2>&1 &
sleep 30
for nd in /controller_server /planner_server /bt_navigator /behavior_server; do
  printf "  %-20s " "$nd"; timeout 6 ros2 lifecycle get "$nd" 2>/dev/null || echo "?"
done
echo "  적재된 레이어:"
timeout 8 ros2 param get /local_costmap/local_costmap plugins 2>/dev/null | sed 's/^/    local  /'
timeout 8 ros2 param get /global_costmap/global_costmap plugins 2>/dev/null | sed 's/^/    global /'
echo "  코스트맵 발행:"
for t in /local_costmap/costmap /global_costmap/costmap; do printf "    %-26s " "$t"; timeout 8 ros2 topic hz "$t" 2>&1 | grep -aoE "average rate: [0-9.]+" | tail -1 || echo 무발행; done
echo "  오류: $(grep -aiE 'error|died|exception' /tmp/nav2.log | tail -3 | cut -c1-130 | tr '\n' ' ')"
