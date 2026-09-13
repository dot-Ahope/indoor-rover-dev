#!/bin/bash
SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
OPT="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=15"
J=jetson@192.168.0.101
tr -d '\r' < $SPS/job305_ghost_stats.py > /tmp/job305.py
sshpass -p <PW> scp $OPT -q /tmp/job305.py $J:/tmp/job305_ghost_stats.py || exit 1
sshpass -p <PW> ssh $OPT $J "ls -d /tmp/bag_* 2>/dev/null | tr '\n' ' '; echo"
for B in bag_v5 bag_v4 bag_s4r7; do
  echo "=== $B 로컬 신규 LETHAL 통계 ==="
  timeout 300 sshpass -p <PW> ssh $OPT $J "source /opt/ros/humble/setup.bash; [ -d /tmp/$B ] && python3 /tmp/job305_ghost_stats.py /tmp/$B /local_costmap/costmap $([ $B = bag_v5 ] && echo map) 2>&1 | grep -av 'Opened database'"
done
echo "=== bag_v5 전역 신규 LETHAL 통계 ==="
timeout 300 sshpass -p <PW> ssh $OPT $J "source /opt/ros/humble/setup.bash; python3 /tmp/job305_ghost_stats.py /tmp/bag_v5 /global_costmap/costmap 2>&1 | grep -av 'Opened database' | head -30"
