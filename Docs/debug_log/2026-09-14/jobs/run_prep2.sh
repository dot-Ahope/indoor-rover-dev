#!/bin/bash
SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
OPT="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=15"
J=jetson@192.168.0.101
for f in job311_floor_noise.py job225_face.py; do tr -d '\r' < $SPS/$f > /tmp/$f; sshpass -p <PW> scp $OPT -q /tmp/$f $J:/tmp/$f || exit 1; done
echo "=== 1. 정면 바닥 잡음 30 s (정지) ==="
timeout 90 sshpass -p <PW> ssh $OPT $J "source /opt/ros/humble/setup.bash; python3 /tmp/job311_floor_noise.py 30 2>&1 | grep -av '^\[INFO\]'"
echo "=== 2. 제자리 정렬 -3.5° (상자 y -0.11 → -0.04 목표) ==="
timeout 90 sshpass -p <PW> ssh $OPT $J "source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash; python3 /tmp/job225_face.py -3.5 1.5 2>&1 | grep -av '^\[INFO\]' | tail -6"
echo "=== 3. 상자 재검출 ==="
timeout 90 sshpass -p <PW> ssh $OPT $J "source /opt/ros/humble/setup.bash; sleep 3; BOX_HINT='1.12 -0.04' python3 /tmp/job248_audit.py 2>&1 | grep -aE '^상자:|근거 없는 셀 위치'; timeout 6 ros2 run tf2_ros tf2_echo map base_link 2>&1 | grep -aE 'Translation|RPY' | head -2"
