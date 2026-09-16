#!/bin/bash
export FASTRTPS_DEFAULT_PROFILES_FILE=$HOME/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml
source /opt/ros/humble/setup.bash
echo "=== slam.log 이유(전체) ==="; grep -a "dropping" /tmp/slam.log | tail -1 | cut -c1-260; echo "  drop 수: $(grep -ac dropping /tmp/slam.log)  slam 시작: $(head -2 /tmp/slam.log | tail -1 | cut -c1-90)"
echo "=== TF 체인 ==="; for pair in "odom base_link" "base_link lidar_link" "base_link sensor_deck_link" "odom lidar_link" "map odom"; do printf "  %-24s " "$pair"; timeout 6 ros2 run tf2_ros tf2_echo $pair 2>&1 | grep -aE "Translation|Invalid|not exist|does not" | head -1 | cut -c1-90; echo; done
echo "=== /scan ==="; printf "  hz: "; timeout 6 ros2 topic hz /scan 2>&1 | grep -aoE "average rate: [0-9.]+" | tail -1; echo; printf "  frame/stamp: "; timeout 6 ros2 topic echo /scan --once 2>/dev/null | grep -aE "frame_id|sec:" | head -3 | tr '\n' ' '; echo; echo "  now: $(date +%s)"
echo "=== tf_static 발행자 ==="; timeout 8 ros2 topic info -v /tf_static 2>/dev/null | grep -aE "Node name|Publisher count" | head -6 | tr '\n' ' '; echo
echo "=== 프로세스 ==="; for p in robot_state_publisher slam_toolbox ekf_node scan_deskew rplidar; do printf "%s:%s " $p $(pgrep -fc $p); done; echo
