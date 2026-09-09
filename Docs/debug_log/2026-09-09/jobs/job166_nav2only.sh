#!/bin/bash
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
sed -i 's/\r$//' /tmp/nav2_params.yaml
cp /tmp/nav2_params.yaml ~/ros2_ws/src/rover_navigation/config/
cp /tmp/nav2_params.yaml ~/ros2_ws/install/rover_navigation/share/rover_navigation/config/
for p in navigation_launch controller_server planner_server bt_navigator behavior_server velocity_smoother smoother_server waypoint_follower lifecycle_manager stuck_monitor; do pkill -TERM -f "$p" 2>/dev/null; done
sleep 6
setsid nohup ros2 launch rover_navigation navigation.launch.py > /tmp/nav2.log 2>&1 &
sleep 32
for nd in /controller_server /planner_server /bt_navigator /behavior_server /velocity_smoother; do
  printf "  %-20s " "$nd"; timeout 6 ros2 lifecycle get "$nd" 2>/dev/null || echo "?"
done
echo "  로컬: $(timeout 8 ros2 param get /local_costmap/local_costmap plugins 2>/dev/null | sed 's/^.*is: //')"
echo "  전역: $(timeout 8 ros2 param get /global_costmap/global_costmap plugins 2>/dev/null | sed 's/^.*is: //')"
for t in /local_costmap/costmap /global_costmap/costmap; do printf "  %-26s " "$t"; timeout 9 ros2 topic hz "$t" 2>&1 | grep -aoE "average rate: [0-9.]+" | tail -1 || echo 무발행; done
echo "=== STVL 초기화 로그 ==="
grep -aiE "stvl|spatio|voxel" /tmp/nav2.log | grep -aiE "Initialized|Using plugin|Subscribed|decay|error|fail" | tail -8 | cut -c1-150 | sed 's/^/  /'
echo "=== 오류 ==="
grep -aiE "error|died|fatal|exception" /tmp/nav2.log | tail -4 | cut -c1-150 | sed 's/^/  /'
echo "=== 부하 ==="
echo "  load: $(cut -d' ' -f1-3 /proc/loadavg)"
top -b -n2 -d1 -o %CPU 2>/dev/null | awk '/PID +USER/{f++} f==2' | head -7 | awk '{printf "    %-18s %6s%%\n", $12, $9}'
