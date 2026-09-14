#!/bin/bash
SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
OPT="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=15"
J=jetson@192.168.0.101
for f in job307_scene.py job308_plan_ab.py; do tr -d '\r' < $SPS/$f > /tmp/$f; sshpass -p <PW> scp $OPT -q /tmp/$f $J:/tmp/$f || exit 1; done
echo "=== 계획 A/B: inflation 0.35/3.0 vs 0.55/2.0 (목표 전방 2.0, 횡 +0.35) ==="
timeout 200 sshpass -p <PW> ssh $OPT $J "source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash; python3 /tmp/job308_plan_ab.py 2.0 0.35 0.55 2.0 2>&1 | grep -av '^\[INFO\]'"
