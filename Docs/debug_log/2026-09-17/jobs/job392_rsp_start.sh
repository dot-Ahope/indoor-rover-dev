#!/bin/bash
export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
ros2 daemon stop >/dev/null 2>&1
echo "잔존 프로세스: $(ps -eo args | grep -aE '/opt/ros/humble/lib|ros2_ws/install' | grep -av grep | cut -c1-80 | tr '\n' ';')"
setsid nohup ros2 launch rover_description description.launch.py > /tmp/description.log 2>&1 &
sleep 6; echo "robot_state_publisher: $(pgrep -fc robot_state_publisher)  lib: $(grep -a libfastrtps /proc/$(pgrep -f robot_state_publisher | head -1)/maps | awk '{print $6}' | sort -u | tr '\n' ' ')"
