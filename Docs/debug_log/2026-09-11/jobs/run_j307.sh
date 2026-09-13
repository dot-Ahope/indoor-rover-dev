#!/bin/bash
SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
OPT="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=15"
J=jetson@192.168.0.101
tr -d '\r' < $SPS/job307_scene.py > /tmp/job307.py
sshpass -p <PW> scp $OPT -q /tmp/job307.py $J:/tmp/job307_scene.py || exit 1
timeout 90 sshpass -p <PW> ssh $OPT $J "source /opt/ros/humble/setup.bash; python3 /tmp/job307_scene.py 2>&1 | grep -av '^\[INFO\]'"
