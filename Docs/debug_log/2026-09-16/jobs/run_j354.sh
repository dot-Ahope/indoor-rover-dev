#!/bin/bash
H=${JETSON_HOST:-172.30.1.8}; SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=10"
tr -d '\r' < $SPS/job354_critics.py > /tmp/job354_critics.py; sshpass -p <PW> scp $O -q /tmp/job354_critics.py jetson@$H:/tmp/ || exit 1
timeout 300 sshpass -p <PW> ssh $O jetson@$H "source /opt/ros/humble/setup.bash; python3 /tmp/job354_critics.py /tmp/bag_${1:-mp4} ${2:-12,16,18,20} 2>&1 | grep -av 'Opened database'"
