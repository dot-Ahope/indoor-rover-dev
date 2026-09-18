#!/bin/bash
export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml
source /opt/ros/humble/setup.bash
for i in 1 2 3; do v=$(timeout 10 ros2 param get /controller_server FollowPathMPPI.temperature 2>&1 | tail -1); echo "temperature: $v"; echo "$v" | grep -q "value is" && break; sleep 2; done
grep -n "^      temperature:" /home/jetson/ros2_ws/install/rover_navigation/share/rover_navigation/config/nav2_params.yaml
