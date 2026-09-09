#!/bin/bash
# 손으로 옮긴 뒤 좌표계 초기화: sensors(EKF) + slam + nav2 재기동. agent/base 는 건드리지 않는다.
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
for p in "navigation_launch" "controller_server" "planner_server" "bt_navigator" "behavior_server" \
         "velocity_smoother" "smoother_server" "waypoint_follower" "lifecycle_manager_navigation" \
         "stuck_monitor" "slam.launch" "slam_toolbox" "sensors.launch" "realsense" "rplidar" \
         "scan_deskew" "ekf_node" "sensor_conditioner" "foxglove"; do
  pkill -9 -f "$p" 2>/dev/null
done
sleep 6
echo "잔존: $(pgrep -fc 'ekf_node|slam_toolbox|realsense|rplidar|controller_server' 2>/dev/null)"
echo "보드 유지 확인: $(ros2 node list 2>/dev/null | grep -a rover_jupiter || echo '없음!')"
echo "=== sensors (자이로 캘리브 ~10s, 정지) ==="
setsid nohup ros2 launch rover_bringup sensors.launch.py > /tmp/sensors.log 2>&1 &
sleep 26
grep -a "gyro bias" /tmp/sensors.log | tail -1 | sed 's/^/  /'
echo "=== slam ==="
setsid nohup ros2 launch rover_bringup slam.launch.py > /tmp/slam.log 2>&1 &
sleep 14
echo "=== nav2 ==="
setsid nohup ros2 launch rover_navigation navigation.launch.py > /tmp/nav2.log 2>&1 &
sleep 28
for nd in /controller_server /planner_server /bt_navigator /behavior_server /velocity_smoother; do
  printf "  %-22s " "$nd"; timeout 6 ros2 lifecycle get "$nd" 2>/dev/null || echo "?"
done
echo "  stuck_monitor: $(ros2 node list 2>/dev/null | grep -a stuck_monitor || echo 없음)"
printf "  %-20s " /wheel_odom; timeout 8 ros2 topic hz /wheel_odom 2>&1 | grep -aoE "average rate: [0-9.]+" | tail -1
printf "  %-20s " /odometry/filtered; timeout 8 ros2 topic hz /odometry/filtered 2>&1 | grep -aoE "average rate: [0-9.]+" | tail -1
echo -n "  map->odom : "; timeout 5 ros2 run tf2_ros tf2_echo map odom 2>/dev/null | grep -aE "Translation" | head -1
echo -n "  odom->base: "; timeout 5 ros2 run tf2_ros tf2_echo odom base_link 2>/dev/null | grep -aE "Translation" | head -1
