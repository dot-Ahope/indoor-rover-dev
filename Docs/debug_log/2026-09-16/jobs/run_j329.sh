#!/bin/bash
SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
OPT="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=15"
J=jetson@${JETSON_HOST:-192.168.0.101}
tr -d '\r' < $SPS/job329_plancorner.py > /tmp/job329_plancorner.py; sshpass -p <PW> scp $OPT -q /tmp/job329_plancorner.py $J:/tmp/ || exit 1
timeout 300 sshpass -p <PW> ssh $OPT $J "source /opt/ros/humble/setup.bash; python3 /tmp/job329_plancorner.py /tmp/bag_${1:-mp2} ${2:-5,24,48,75} 2>&1 | grep -av 'Opened database'"
