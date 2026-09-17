#!/bin/bash
H=${JETSON_HOST:-172.30.1.8}; SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=10"
RJ=run_j.sh; [ "$H" = "172.30.1.8" ] && RJ=run_j_alt.sh
echo "=== 1. 재기동 ($H) ==="; bash $SPS/$RJ job240_clean.sh 15 2>&1 | grep -aE '에이전트|세션|무발행|wheel_odom|gyro|map->odom|자세|중단'
echo "=== 2. 릴레이·readback·상자 게이트 ==="; JETSON_HOST=$H bash $SPS/run_gate2.sh 1.21 0.0 2>&1 | grep -avE 'FollowPathMPPI\.(time_steps|model_dt)|stuck_monitor 파라미터|:2 '
for f in job377_goalclear.py job386_slamalive.py job403_critics_rb.sh; do tr -d '\r' < $SPS/$f > /tmp/$f; sshpass -p <PW> scp $O -q /tmp/$f jetson@$H:/tmp/$f || exit 1; done
echo "=== 3. 목표 근처 크리틱·SLAM·목표 여유 ==="; timeout 150 sshpass -p <PW> ssh $O jetson@$H "bash /tmp/job403_critics_rb.sh"
