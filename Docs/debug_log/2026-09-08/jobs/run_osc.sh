#!/bin/bash
# 사용: run_osc.sh <csv이름> <x> <y> <yaw> <timeout>
SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
OPT="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=6"
N=$1; shift
for t in $(seq 1 8); do sshpass -p <PW> scp $OPT -q $SPS/job56_osc.py jetson@192.168.0.101:/tmp/ 2>/dev/null && break; sleep 4; done
for t in 1 2 3; do
  if timeout 300 sshpass -p <PW> ssh $OPT jetson@192.168.0.101 "source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash; python3 /tmp/job56_osc.py $* $N 2>&1"; then break; fi
  echo "(재시도 $t)"; sleep 5
done
for t in $(seq 1 6); do sshpass -p <PW> scp $OPT -q jetson@192.168.0.101:/tmp/$N.csv $SPS/ 2>/dev/null && { echo "csv 회수: $N.csv"; break; }; sleep 4; done
