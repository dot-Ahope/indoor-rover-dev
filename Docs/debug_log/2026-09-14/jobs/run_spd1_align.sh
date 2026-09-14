#!/bin/bash
SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
OPT="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=15"
J=jetson@192.168.0.101
echo "=== 1. 릴레이 고아 정리 ==="
bash $SPS/run_j.sh job314_relay_orphan.sh 2>&1 | grep -avE '^\[INFO\]'
echo "=== 2. 회전 게이트 (job228 제자리 회전 투영) ==="
timeout 60 sshpass -p <PW> ssh $OPT $J "source /opt/ros/humble/setup.bash; python3 /tmp/job228_why.py 2>&1 | sed -n '/제자리 회전 투영/,/라이다 방위별/p' | grep -aE '회전|^ +[-+] ?[0-9]+ ' | head -12"
echo "=== 3. 정렬 +3.3° (상자 y +0.026 → -0.04) 후 재검출 ==="
timeout 90 sshpass -p <PW> ssh $OPT $J "source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash; python3 /tmp/job225_face.py 3.3 1.5 2>&1 | tail -2; sleep 3; BOX_HINT='1.14 -0.04' python3 /tmp/job248_audit.py 2>&1 | grep -aE '^상자:'"
