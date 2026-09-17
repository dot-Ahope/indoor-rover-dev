#!/bin/bash
# Jetson /tmp 로그를 스크래치패드로 회수: 인자 PREFIX
H=${JETSON_HOST:-192.168.0.101}; SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=10"
for f in slam.log nav2.log sensors.log base.log; do
  sshpass -p <PW> scp $O -q jetson@$H:/tmp/$f $SPS/${1:-x}_$f && echo "$f $(wc -c < $SPS/${1:-x}_$f) B"
done
