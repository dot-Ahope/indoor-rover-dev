#!/bin/bash
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
sleep 20
for nd in /controller_server /planner_server /bt_navigator /behavior_server /velocity_smoother; do
  printf "  %-20s " "$nd"; timeout 6 ros2 lifecycle get "$nd" 2>/dev/null || echo "?"
done
for t in /local_costmap/costmap /global_costmap/costmap; do printf "  %-26s " "$t"; timeout 9 ros2 topic hz "$t" 2>&1 | grep -aoE "average rate: [0-9.]+" | tail -1 || echo 무발행; done
echo "  오류: $(grep -aiE 'error|died|fatal' /tmp/nav2.log | tail -3 | cut -c1-140 | tr '\n' ' ')"
echo "  EKF 위반: $(grep -ac 'Failed to meet update rate' /tmp/sensors.log 2>/dev/null)회 | slam 폐기: $(grep -ac 'Message Filter dropping' /tmp/slam.log 2>/dev/null)회 | load: $(cut -d' ' -f1-3 /proc/loadavg)"
