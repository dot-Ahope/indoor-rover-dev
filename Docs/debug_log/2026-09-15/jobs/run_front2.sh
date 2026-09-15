#!/bin/bash
SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
OPT="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=15"
J=jetson@192.168.0.101
tr -d '\r' < $SPS/job322_snap.py > /tmp/job322.py; sshpass -p <PW> scp $OPT -q /tmp/job322.py $J:/tmp/job322_snap.py
timeout 200 sshpass -p <PW> ssh $OPT $J "source /opt/ros/humble/setup.bash; python3 /tmp/job322_snap.py 2>&1 | tail -1; echo '=== 상자 앞 띠 (필터, 40 s) ==='; TOPIC=/camera/depth/points_filtered python3 -u /tmp/job320_boxfront.py 1.17 0.063 40 2>&1 | grep -av '^\[INFO\]'; echo '=== 상자 띠 (필터, 12 s) ==='; TOPIC=/camera/depth/points_filtered ZTH=0.08 python3 /tmp/job312_box_edge.py 1.17 0.063 12 2>&1 | grep -aE '^  (핵심|좌측|앞쪽|우측)|코스트맵'; grep -a '프레임:' /tmp/sensors.log | tail -1 | grep -aoE '입력.*'"
sshpass -p <PW> scp $OPT -q $J:/tmp/snap.jpg $SPS/snap_mp2.jpg && echo "snap 회수 OK"
