#!/bin/bash
H=${JETSON_HOST:-172.30.1.8}; SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=10"
tr -d '\r' < $SPS/job345_traj.py > /tmp/job345_traj.py; sshpass -p <PW> scp $O -q /tmp/job345_traj.py jetson@$H:/tmp/ || exit 1
timeout 300 sshpass -p <PW> ssh $O jetson@$H "export FASTRTPS_DEFAULT_PROFILES_FILE=$HOME/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; echo '=== syslog Sep 16 15:5x wifi ==='; grep -aE '^Sep 16 15:5[5-9]|^Sep 16 16:0[01]' /var/log/syslog | grep -aiE 'wpa_supplicant|wlP1p1s0' | grep -aiE 'deauth|disconnect|reason|AUTH|CTRL-EVENT|associated|activated' | head -10 | cut -c1-170; echo '=== job345 ==='; python3 /tmp/job345_traj.py /tmp/bag_mp4 6,9,12,14,16,17,18,19,20,21,22,23 2>&1 | grep -av 'Opened database'"
