#!/bin/bash
# 손 이동 후 좌표계 초기화 + 설정 반영. SIGTERM 우선 (SIGKILL 은 FastDDS 공유메모리 잔재를
# 남겨 퍼블리셔가 그래프에서 사라지는 사고를 낸다 — 2026-09-09 실측).
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
sed -i 's/\r$//' /tmp/nav2_params.yaml
cp /tmp/nav2_params.yaml ~/ros2_ws/src/rover_navigation/config/
cp /tmp/nav2_params.yaml ~/ros2_ws/install/rover_navigation/share/rover_navigation/config/
echo "배포: depth clearing false $(grep -c 'clearing: false' ~/ros2_ws/install/rover_navigation/share/rover_navigation/config/nav2_params.yaml)곳"

NODES="navigation_launch controller_server planner_server bt_navigator behavior_server \
velocity_smoother smoother_server waypoint_follower lifecycle_manager stuck_monitor \
slam_toolbox ekf_node sensor_conditioner scan_deskew rplidar realsense foxglove"
echo "=== SIGTERM 종료 ==="
pkill -TERM -f "sensors.launch" 2>/dev/null; pkill -TERM -f "slam.launch" 2>/dev/null
pkill -TERM -f "navigation.launch" 2>/dev/null
for p in $NODES; do pkill -TERM -f "$p" 2>/dev/null; done
for i in $(seq 1 12); do
  [ "$(pgrep -fc 'ekf_node|slam_toolbox|realsense|rplidar|foxglove|sensor_conditioner|controller_server' 2>/dev/null || echo 0)" = "0" ] && break
  sleep 1
done
echo "  잔존: $(pgrep -fc 'ekf_node|slam_toolbox|realsense|rplidar|foxglove|sensor_conditioner|controller_server' 2>/dev/null || echo 0)"
echo "  fastrtps 잔재: $(ls /dev/shm 2>/dev/null | grep -c fastrtps)"
echo "  보드 유지: $(ros2 node list 2>/dev/null | grep -a rover_jupiter || echo '없음!')"
echo "=== sensors (자이로 캘리브 ~10s, 정지) ==="
setsid nohup ros2 launch rover_bringup sensors.launch.py > /tmp/sensors.log 2>&1 &
sleep 26
grep -a "gyro bias" /tmp/sensors.log | tail -1 | sed 's/^/  /'
echo "=== slam ==="; setsid nohup ros2 launch rover_bringup slam.launch.py > /tmp/slam.log 2>&1 &
sleep 14
echo "=== nav2 ==="; setsid nohup ros2 launch rover_navigation navigation.launch.py > /tmp/nav2.log 2>&1 &
sleep 28
for nd in /controller_server /planner_server /bt_navigator /behavior_server; do
  printf "  %-20s " "$nd"; timeout 6 ros2 lifecycle get "$nd" 2>/dev/null || echo "?"
done
printf "  %-20s " /odometry/filtered; timeout 8 ros2 topic hz /odometry/filtered 2>&1 | grep -aoE "average rate: [0-9.]+" | tail -1
echo -n "  odom->base: "; timeout 5 ros2 run tf2_ros tf2_echo odom base_link 2>/dev/null | grep -aE "Translation" | head -1
echo "  clearing 적용값: $(timeout 6 ros2 param get /local_costmap/local_costmap voxel_layer.depth.clearing 2>/dev/null | sed 's/^.*is: //')"
