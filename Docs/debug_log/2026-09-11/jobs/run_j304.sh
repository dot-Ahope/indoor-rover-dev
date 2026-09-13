#!/bin/bash
SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
OPT="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=15"
J=jetson@192.168.0.101
tr -d '\r' < $SPS/job304_lethal_audit.py > /tmp/job304.py
sshpass -p <PW> scp $OPT -q /tmp/job304.py $J:/tmp/job304_lethal_audit.py || exit 1
echo "=== v5 로컬 @ 첫 충돌 ==="
timeout 300 sshpass -p <PW> ssh $OPT $J "source /opt/ros/humble/setup.bash; python3 /tmp/job304_lethal_audit.py /tmp/bag_v5 1789116145.96 -0.050 -0.016 -2.9 2>&1 | grep -av 'Opened database'"
echo "=== v5 전역 @ 첫 충돌 ==="
timeout 300 sshpass -p <PW> ssh $OPT $J "source /opt/ros/humble/setup.bash; python3 /tmp/job304_lethal_audit.py /tmp/bag_v5 1789116145.96 -0.050 -0.016 -2.9 /global_costmap/costmap 2>&1 | grep -av 'Opened database' | grep -av '^bag 토픽'"
echo "=== v5 로컬 @ 출발 +3 s ==="
timeout 300 sshpass -p <PW> ssh $OPT $J "source /opt/ros/humble/setup.bash; python3 /tmp/job304_lethal_audit.py /tmp/bag_v5 1789116123.9 -0.050 -0.016 -2.9 2>&1 | grep -av 'Opened database' | grep -av '^bag 토픽'"
