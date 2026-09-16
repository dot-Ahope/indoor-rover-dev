#!/bin/bash
SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
OPT="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=15"
J=jetson@${JETSON_HOST:-192.168.0.101}
tr -d '\r' < $SPS/job312_box_edge.py > /tmp/job312_box_edge.py; sshpass -p <PW> scp $OPT -q /tmp/job312_box_edge.py $J:/tmp/ || exit 1
timeout 200 sshpass -p <PW> ssh $OPT $J "source /opt/ros/humble/setup.bash; echo '##### RAW /camera/camera/depth/color/points'; TOPIC=/camera/camera/depth/color/points python3 /tmp/job312_box_edge.py $1 $2 ${3:-30} 2>&1 | grep -av '^\['; echo '##### FILTERED /camera/depth/points_filtered'; TOPIC=/camera/depth/points_filtered python3 /tmp/job312_box_edge.py $1 $2 ${3:-30} 2>&1 | grep -av '^\['"
