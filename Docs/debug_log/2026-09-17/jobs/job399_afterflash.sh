#!/bin/bash
export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml
source /opt/ros/humble/setup.bash
echo "now $(date +%T)"
echo "=== 에이전트 세션 로그(최근) ==="; docker logs --since 20m microros_agent 2>&1 | grep -aiE "session|established|client" | tail -4 | sed 's/\x1b\[[0-9;]*m//g' | cut -c1-140
for t in /wheel_odom /rover/status /odometry/filtered; do printf "  %-20s " $t; timeout 6 ros2 topic hz $t 2>&1 | grep -aoE "average rate: [0-9.]+" | tail -1; echo; done
printf "보드 상태: "; timeout 5 ros2 topic echo /rover/status --once 2>/dev/null | grep -aE "value:" | head -2 | tr -s ' ' | cut -c1-160 | tr '\n' ' '; echo
printf "map->base 지금: "; timeout 8 ros2 run tf2_ros tf2_echo map base_link 2>&1 | grep -aE "Translation|RPY \(degree\)" | head -2 | tr '\n' ' '; echo
echo "(mp8 종료 때: map (1.960, 0.240), yaw +0.6°)"
echo "=== stuck_monitor 로그(최근 20분) ==="; grep -a "stuck_monitor" /tmp/nav2.log | tail -3 | cut -c1-170
echo "=== sensors.log 자이로/EKF 경고(최근) ==="; tail -3 /tmp/sensors.log | cut -c1-150
