#!/bin/bash
export FASTRTPS_DEFAULT_PROFILES_FILE=$HOME/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
sed -i 's/\r$//' /tmp/nav2_params.yaml
cp /tmp/nav2_params.yaml ~/ros2_ws/src/rover_navigation/config/
cp /tmp/nav2_params.yaml ~/ros2_ws/install/rover_navigation/share/rover_navigation/config/
echo "설정 되돌림: clearing true $(grep -c 'clearing: true' ~/ros2_ws/install/rover_navigation/share/rover_navigation/config/nav2_params.yaml)곳"
echo -n "종료 전 배터리: "; timeout 6 ros2 topic echo /battery --once 2>/dev/null | grep -aoE "voltage: [0-9.]+"
echo "=== 모터 정지 ==="
for i in $(seq 1 12); do ros2 topic pub -1 /cmd_vel geometry_msgs/msg/Twist "{}" >/dev/null 2>&1; done
echo "=== SIGTERM 종료 (SIGKILL 금지) ==="
pkill -TERM -f "ros2 launch" 2>/dev/null
for p in navigation_launch controller_server planner_server bt_navigator behavior_server velocity_smoother smoother_server waypoint_follower lifecycle_manager stuck_monitor slam_toolbox ekf_node sensor_conditioner scan_deskew rplidar realsense foxglove robot_state_publisher; do pkill -TERM -f "$p" 2>/dev/null; done
for i in $(seq 1 15); do
  [ "$(pgrep -fc 'ekf_node|slam_toolbox|realsense|rplidar|foxglove|sensor_conditioner|controller_server|robot_state_publisher' 2>/dev/null || echo 0)" = "0" ] && break
  sleep 1
done
echo "  잔존: $(pgrep -fc 'ekf_node|slam_toolbox|realsense|rplidar|foxglove|sensor_conditioner|controller_server|robot_state_publisher' 2>/dev/null || echo 0)"
docker rm -f microros_agent >/dev/null 2>&1 && echo "  agent 종료" || echo "  agent 없음"
ros2 daemon stop >/dev/null 2>&1; sleep 2
rm -f /dev/shm/fastrtps_* /dev/shm/sem.fastrtps_* 2>/dev/null
echo "  fastrtps 잔재: $(ls /dev/shm 2>/dev/null | grep -c fastrtps)"
echo "  ROS 프로세스: $(ps -eo args 2>/dev/null | grep -aiE 'opt/ros|ros2_ws' | grep -avc grep)   docker: $(docker ps -q | wc -l)"
echo "  load: $(cut -d' ' -f1-3 /proc/loadavg)"
echo "완료 — 충전 진행하셔도 됩니다"
