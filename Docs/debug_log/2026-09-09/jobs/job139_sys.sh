#!/bin/bash
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "load: $(cut -d' ' -f1-3 /proc/loadavg)   코어 $(nproc)"
echo "중복 점검:"
for p in ekf_node slam_toolbox realsense rplidar sensor_conditioner scan_deskew foxglove controller_server planner_server bt_navigator robot_state_publisher; do
  c=$(pgrep -fc "$p" 2>/dev/null || echo 0); [ "$c" != "0" ] && printf "  %-22s %s\n" "$p" "$c"
done
echo ""
printf "  %-14s " /tf;        timeout 8 ros2 topic hz /tf 2>&1 | grep -aoE "average rate: [0-9.]+" | tail -1 || echo 무발행
printf "  %-14s " /tf_static; timeout 8 ros2 topic hz /tf_static 2>&1 | grep -aoE "average rate: [0-9.]+" | tail -1 || echo 무발행
printf "  %-14s " /odometry/filtered; timeout 8 ros2 topic hz /odometry/filtered 2>&1 | grep -aoE "average rate: [0-9.]+" | tail -1 || echo 무발행
printf "  %-14s " /map;       timeout 10 ros2 topic hz /map 2>&1 | grep -aoE "average rate: [0-9.]+" | tail -1 || echo 무발행
echo ""
echo "=== /tf 에 실린 변환 ==="
timeout 6 ros2 topic echo /tf --once 2>/dev/null | grep -aE "child_frame_id|frame_id" | sed 's/^/  /' | head -8
echo ""
echo "=== 상위 CPU ==="
top -b -n2 -d1 -o %CPU 2>/dev/null | awk '/PID +USER/{f++} f==2' | head -8 | awk '{printf "  %-18s %6s%%\n", $12, $9}'
echo "=== 온도/스로틀 ==="
cat /sys/devices/virtual/thermal/thermal_zone*/temp 2>/dev/null | head -4 | awk '{printf "  %.1f°C\n", $1/1000}'
echo "=== 배터리 ==="
timeout 5 ros2 topic echo /battery --once 2>/dev/null | grep -aoE "voltage: [0-9.]+"
