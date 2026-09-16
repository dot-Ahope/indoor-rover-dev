#!/bin/bash
SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
OPT="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=15"
J=jetson@${JETSON_HOST:-192.168.0.101}
tr -d '\r' < $SPS/job340_smooth_ab.py > /tmp/job340_smooth_ab.py; sshpass -p <PW> scp $OPT -q /tmp/job340_smooth_ab.py $J:/tmp/ || exit 1
timeout 200 sshpass -p <PW> ssh $OPT $J "source /opt/ros/humble/setup.bash; python3 /tmp/job340_smooth_ab.py ${1:-1.8} ${2:-0.0} ${3:-1.16} ${4:-0.05} ${5:-0.70} 2>&1 | grep -av '^\['"
