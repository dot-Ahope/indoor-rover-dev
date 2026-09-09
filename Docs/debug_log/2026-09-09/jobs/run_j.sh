#!/bin/bash
# 범용 러너: $1 = 스크립트 파일명 (스크래치패드 기준), 나머지 = 인자
SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
OPT="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=8"
F=$1; shift
sshpass -p <PW> scp $OPT -q $SPS/$F jetson@192.168.0.101:/tmp/ || exit 1
case "$F" in
  *.py) CMD="python3 /tmp/$F $*" ;;
  *)    CMD="bash /tmp/$F $*" ;;
esac
timeout 300 sshpass -p <PW> ssh $OPT jetson@192.168.0.101 "source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash; $CMD 2>&1 | tail -60"
