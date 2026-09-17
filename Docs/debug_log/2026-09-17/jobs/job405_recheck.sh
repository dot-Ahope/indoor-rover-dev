#!/bin/bash
export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml
source /opt/ros/humble/setup.bash
for i in 1 2 3; do printf "SLAM #%s: " $i; python3 /tmp/job386_slamalive.py 2>&1 | grep -av '^\[' | tr '\n' ' '; echo; sleep 2; done
for p in FollowPathMPPI.PathFollowCritic.threshold_to_consider FollowPathMPPI.visualize; do printf "  %-50s %s\n" $p "$(timeout 10 ros2 param get /controller_server $p 2>&1 | tail -1)"; done
echo "load $(cut -d' ' -f1-3 /proc/loadavg)"
