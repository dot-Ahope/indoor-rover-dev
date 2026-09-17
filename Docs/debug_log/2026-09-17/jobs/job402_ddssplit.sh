#!/bin/bash
export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml
source /opt/ros/humble/setup.bash
ros2 daemon stop >/dev/null 2>&1
for t in /wheel_odom /rover/status /scan /odometry/filtered /camera/depth/points_filtered; do printf "  %-32s " $t; timeout 7 ros2 topic hz $t 2>&1 | grep -aoE "average rate: [0-9.]+" | tail -1 || true; echo; done
printf "  map->base: "; timeout 7 ros2 run tf2_ros tf2_echo map base_link 2>&1 | grep -aE "Translation|does not exist" | head -1
