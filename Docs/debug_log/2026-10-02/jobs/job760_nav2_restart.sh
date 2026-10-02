#!/bin/bash
# 10-01 §8.18: Nav2 만 재시작(새 BT 적용) — 센서·EKF·위치 추정(slam_toolbox)·에이전트는 그대로(로버가 손으로 옮겨지지 않아 위치 추정 유효).
#   stuck_monitor 관찰 모드(§8.12). nvblox 는 navigation.launch 가 함께 띄움.
set +u
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml
echo "== 재시작 전 위치: $(timeout 8 ros2 run tf2_ros tf2_echo map base_link 2>&1 | grep -a Translation | head -1)"
P="navigation.launch controller_server planner_server bt_navigator behavior_server velocity_smoother smoother_server waypoint_follower lifecycle_manager stuck_monitor nav_guard nvblox_up.sh"
for p in $P; do pkill -f "$p" 2>/dev/null; done
docker exec isaac_ros_dev-aarch64-container bash -c "pkill -f nvblox_node" 2>/dev/null
for i in $(seq 1 15); do n=0; for p in $P; do n=$((n+$(pgrep -fc "$p"))); done; [ $n = 0 ] && break; sleep 1; done
echo "  정리 후 남은 Nav2 프로세스: $n | slam $(pgrep -fc localization_slam) · ekf $(pgrep -fc ekf_node)"
setsid nohup ros2 launch rover_navigation navigation.launch.py stuck_shadow:=true nav_map:=/home/jetson/maps/office/office_v3.yaml > /tmp/nav2.log 2>&1 &
sleep 35
for nd in /controller_server /planner_server /bt_navigator /behavior_server; do printf "  %-20s " "$nd"; timeout 8 ros2 lifecycle get "$nd" 2>/dev/null || echo "?"; done
echo "  BT IsPathValid: $(grep -c IsPathValid ~/ros2_ws/install/rover_navigation/share/rover_navigation/config/nav_to_pose_no_spin.xml) · stuck shadow: $(timeout 10 ros2 param get /stuck_monitor shadow_mode 2>&1 | tail -1) · nav_guard $(pgrep -fc nav_guard.py)"
echo "== 재시작 뒤 위치: $(timeout 8 ros2 run tf2_ros tf2_echo map base_link 2>&1 | grep -a Translation | head -1) | load $(cut -d' ' -f1-3 /proc/loadavg)"
grep -aiE "error|fail" /tmp/nav2.log | grep -av "Message Filter" | head -5 | cut -c1-200
