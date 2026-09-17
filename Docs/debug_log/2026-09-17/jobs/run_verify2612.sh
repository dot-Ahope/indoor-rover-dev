#!/bin/bash
H=${JETSON_HOST:-192.168.0.101}; SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=10 -o ServerAliveInterval=5"
for f in job392_rsp_start.sh job393_churn.sh job386_slamalive.py; do tr -d '\r' < $SPS/$f > /tmp/$f; sshpass -p <PW> scp $O -q /tmp/$f jetson@$H:/tmp/$f || exit 1; done
echo "=== rsp ==="; timeout 60 sshpass -p <PW> ssh $O jetson@$H "bash /tmp/job392_rsp_start.sh"
echo "=== job240 ==="; bash $SPS/run_j.sh job240_clean.sh 15 2>&1 | grep -aE '에이전트|세션|무발행|wheel_odom|gyro|map->odom|자세|중단'
echo "=== churn ==="; timeout 400 sshpass -p <PW> ssh $O jetson@$H "bash /tmp/job393_churn.sh"
