#!/bin/bash
H=${JETSON_HOST:-192.168.0.101}; SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=10"
tr -d '\r' < $SPS/job394_cmdtrace.py > /tmp/job394_cmdtrace.py; sshpass -p <PW> scp $O -q /tmp/job394_cmdtrace.py jetson@$H:/tmp/ || exit 1
timeout 200 sshpass -p <PW> ssh $O jetson@$H "source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash; python3 /tmp/job394_cmdtrace.py /tmp/bag_mp8 1789613137.649 2>&1 | grep -av 'Opened database'"
