#!/bin/bash
H=${JETSON_HOST:-172.30.1.8}; SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=10"
tr -d '\r' < $SPS/job416_boxclear.py > /tmp/job416_boxclear.py; sshpass -p <PW> scp $O -q /tmp/job416_boxclear.py jetson@$H:/tmp/ || exit 1
timeout 400 sshpass -p <PW> ssh $O jetson@$H "source /opt/ros/humble/setup.bash; ls -d /tmp/bag_mp12* 2>&1; B=\$(ls -d /tmp/bag_mp12 2>/dev/null || ls -d /tmp/bag_mp12* | head -1); python3 /tmp/job416_boxclear.py \$B 1789631920.2186 2>&1 | grep -av 'Opened database'"
