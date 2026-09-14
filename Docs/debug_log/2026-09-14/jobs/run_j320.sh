#!/bin/bash
SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
OPT="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=15"
J=jetson@192.168.0.101
tr -d '\r' < $SPS/job320_boxfront.py > /tmp/job320.py; sshpass -p <PW> scp $OPT -q /tmp/job320.py $J:/tmp/job320_boxfront.py || exit 1
BXF=$(awk "BEGIN{print $1-0.30}")
timeout 200 sshpass -p <PW> ssh $OPT $J "source /opt/ros/humble/setup.bash; python3 -u /tmp/job320_boxfront.py $1 $2 60 2>&1 | grep -av '^\[INFO\]'; echo '--- 원본 토픽 ---'; TOPIC=/camera/camera/depth/color/points python3 -u /tmp/job320_boxfront.py $1 $2 45 2>&1 | grep -av '^\[INFO\]'; echo '--- 로컬 코스트맵 상자 앞 셀 ---'; python3 /tmp/job315_boxcells.py $BXF $2 2>&1 | tail -1"
