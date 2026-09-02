#!/bin/bash
# Nav2 기동 + 검증 (주행 없음)
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "=== 전제 스택 확인 ==="
for t in /wheel_odom /odometry/filtered /scan /map; do
  printf "  %-22s " "$t"; timeout 5 ros2 topic hz "$t" 2>&1 | grep -aoE "average rate: [0-9.]+" | head -1 || echo "무발행!"
done
echo -n "  map->odom TF: "; timeout 5 ros2 run tf2_ros tf2_echo map odom 2>/dev/null | grep -aE "Translation" | head -1 || echo "없음"
echo ""
echo "=== Nav2 기동 ==="
pkill -f "navigation_launch\|controller_server\|planner_server\|bt_navigator\|behavior_server\|velocity_smoother\|smoother_server\|waypoint_follower\|lifecycle_manager_navigation" 2>/dev/null; sleep 2
setsid nohup ros2 launch rover_navigation navigation.launch.py > /tmp/nav2.log 2>&1 &
sleep 25
echo "=== 노드 ==="
ros2 node list 2>/dev/null | grep -E "controller_server|planner_server|bt_navigator|behavior_server|velocity_smoother|smoother_server|waypoint_follower|lifecycle_manager" | sed 's/^/  /'
echo ""
echo "=== lifecycle 상태 ==="
for nd in /controller_server /planner_server /bt_navigator /behavior_server /velocity_smoother; do
  printf "  %-22s " "$nd"; timeout 6 ros2 lifecycle get "$nd" 2>/dev/null || echo "?"
done
echo ""
echo "=== costmap 발행 ==="
for t in /local_costmap/costmap /global_costmap/costmap; do
  printf "  %-26s " "$t"; timeout 8 ros2 topic hz "$t" 2>&1 | grep -aoE "average rate: [0-9.]+" | head -1 || echo "무발행"
done
echo ""
echo "=== 오류 로그 (있으면) ==="
grep -aiE "error|fail|exception|refus" /tmp/nav2.log | grep -av "0 errors" | tail -8 || echo "  (없음)"
echo ""
echo "=== CPU/부하 ==="
echo "  load: $(cat /proc/loadavg | cut -d' ' -f1-3)"
top -b -n2 -d1 -o %CPU | awk '/PID +USER/{f++} f==2' | head -7 | awk '{printf "    %-16s %5s%%\n",$12,$9}'
