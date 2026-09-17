#!/bin/bash
H=${JETSON_HOST:-192.168.0.101}; SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=10"
echo "=== 1. 재기동 ==="; bash $SPS/run_j.sh job240_clean.sh 15 2>&1 | grep -aE '에이전트|세션|무발행|wheel_odom|gyro|map->odom|자세|중단'
echo "=== 2. 릴레이·readback·게이트 ==="; bash $SPS/run_gate2.sh 1.34 -0.05 2>&1 | grep -avE 'FollowPathMPPI\.(time_steps|visualize|model_dt)|stuck_monitor 파라미터'
for f in job377_goalclear.py job378_goalcands.sh; do tr -d '\r' < $SPS/$f > /tmp/$f; sshpass -p <PW> scp $O -q /tmp/$f jetson@$H:/tmp/$f || exit 1; done
echo "=== 3. BT·목표 후보 ==="; timeout 200 sshpass -p <PW> ssh $O jetson@$H "bash /tmp/job378_goalcands.sh"
