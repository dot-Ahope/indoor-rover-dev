#!/bin/bash
export FASTRTPS_DEFAULT_PROFILES_FILE=$HOME/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml
source /opt/ros/humble/setup.bash
echo "=== robot_state_publisher 고아 정리 ==="; ps -eo pid,etimes,args --sort=etimes | grep -a robot_state_publisher | grep -av grep | cut -c1-80
N=$(pgrep -fc robot_state_publisher); if [ "$N" -gt 1 ]; then OLD=$(pgrep -f robot_state_publisher | head -n $((N-1)) | tr '\n' ' '); for p in $(ps -eo pid,etimes --sort=-etimes | grep -aE "^ *($(pgrep -f robot_state_publisher | tr '\n' '|' | sed 's/|$//')) " | head -n $((N-1)) | awk '{print $1}'); do kill -TERM $p && echo "  고아 $p 종료"; done; fi
sleep 2; echo "  남은 rsp: $(pgrep -fc robot_state_publisher)"
echo "=== TF/SLAM ==="; printf "  odom->base: "; timeout 8 ros2 run tf2_ros tf2_echo odom base_link 2>&1 | grep -a Translation | head -1; printf "  map->odom: "; timeout 8 ros2 run tf2_ros tf2_echo map odom 2>&1 | grep -a Translation | head -1
echo "  slam: $(pgrep -fc slam_toolbox)  slam.log 끝: $(tail -1 /tmp/slam.log | cut -c1-100)"
echo "=== Wi-Fi 최근 deauth ==="; grep -aE "^Sep 16 1[67]:" /var/log/syslog | grep -aiE "CTRL-EVENT-DISCONNECTED|AUTH_FAILED" | tail -3 | cut -c1-120; echo "  ip: $(ip -4 -o addr show wlP1p1s0 | awk '{print $4}')"
echo "=== yaml PathFollow ==="; grep -o "PathFollowCritic: {[^}]*}" ~/ros2_ws/install/rover_navigation/share/rover_navigation/config/nav2_params.yaml
