#!/bin/bash
SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
OPT="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=15"
J=jetson@${JETSON_HOST:-192.168.0.101}
for f in job327_mp2why.py job334_rate.sh; do tr -d '\r' < $SPS/$f > /tmp/$f; sshpass -p <PW> scp $OPT -q /tmp/$f $J:/tmp/$f || exit 1; done
timeout 400 sshpass -p <PW> ssh $OPT $J "bash /tmp/job334_rate.sh ${2:-1789525870}; source /opt/ros/humble/setup.bash; python3 /tmp/job327_mp2why.py /tmp/bag_${1:-mp3} 0 0 0 ${3:-30,60,80,85} 2>&1 | grep -av 'Opened database'"
