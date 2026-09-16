#!/bin/bash
H=${JETSON_HOST:-172.30.1.8}; SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=10 -o ServerAliveInterval=5"
for f in nav_to_pose_no_spin.xml job363_rsp.sh job240_clean.sh job348_readback2.sh; do tr -d '\r' < $SPS/$f > /tmp/$f; sshpass -p <PW> scp $O -q /tmp/$f jetson@$H:/tmp/$f || { echo "scp 실패 $f"; exit 1; }; done
timeout 120 sshpass -p <PW> ssh $O jetson@$H "bash /tmp/job363_rsp.sh"
echo "=== job240 (에이전트 유지) ==="
timeout 400 sshpass -p <PW> ssh $O jetson@$H "bash /tmp/job240_clean.sh 15" 2>&1 | grep -aE "에이전트|wheel_odom|gyro|map->odom|자세|상자:|최소폭|단일|프로세스|무발행|중단"
echo "=== readback ==="; timeout 120 sshpass -p <PW> ssh $O jetson@$H "bash /tmp/job348_readback2.sh" 2>&1 | grep -aE "raw_path|nav2:|자세|temperature"
