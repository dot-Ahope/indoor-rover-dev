#!/bin/bash
SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
OPT="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=15"
J=jetson@${JETSON_HOST:-192.168.0.101}
tr -d '\r' < $SPS/job322_snap.py > /tmp/job322_snap.py; sshpass -p <PW> scp $OPT -q /tmp/job322_snap.py $J:/tmp/ || exit 1
timeout 40 sshpass -p <PW> ssh $OPT $J "source /opt/ros/humble/setup.bash; python3 /tmp/job322_snap.py 2>&1 | grep -av '^\['; echo -n 'odom pose: '; timeout 6 ros2 run tf2_ros tf2_echo odom base_link 2>&1 | grep -a Translation | head -1; echo -n 'map pose: '; timeout 6 ros2 run tf2_ros tf2_echo map base_link 2>&1 | grep -a Translation | head -1"
sshpass -p <PW> scp $OPT -q $J:/tmp/snap.jpg $SPS/snap_$(date +%H%M%S).jpg && ls -t $SPS/snap_*.jpg | head -1
