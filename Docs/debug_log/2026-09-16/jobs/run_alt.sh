#!/bin/bash
# 대체 호스트(172.30.1.8)로 스크립트 실행 + bag/csv 회수
H=${JETSON_HOST:-172.30.1.8}; SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=10"
tr -d '\r' < $SPS/$1 > /tmp/$1; sshpass -p <PW> scp $O -q /tmp/$1 jetson@$H:/tmp/$1 || { echo "scp 실패 $H"; exit 1; }
timeout 120 sshpass -p <PW> ssh $O jetson@$H "export FASTRTPS_DEFAULT_PROFILES_FILE=$HOME/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml; bash /tmp/$1"
if [ -n "$2" ]; then sshpass -p <PW> scp $O -q jetson@$H:/tmp/bag_$2.tgz $SPS/bags/bag_$2.tgz && echo "bag 회수 OK $(stat -c %s $SPS/bags/bag_$2.tgz)"; sshpass -p <PW> scp $O -q jetson@$H:/tmp/$2.csv $SPS/$2.csv && echo "csv 회수 OK"; sshpass -p <PW> scp $O -q jetson@$H:/tmp/drive_$2.log $SPS/drive_$2_remote.log && echo "drive log 회수 OK"; fi
