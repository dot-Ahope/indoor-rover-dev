#!/bin/bash
H=${JETSON_HOST:-172.30.1.8}; SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=10"
for f in job353_stop2.sh job240_clean.sh; do tr -d '\r' < $SPS/$f > /tmp/$f; sshpass -p <PW> scp $O -q /tmp/$f jetson@$H:/tmp/$f || { echo "scp 실패 $f"; exit 1; }; done
echo "=== 정지 ==="; timeout 90 sshpass -p <PW> ssh $O jetson@$H "bash /tmp/job353_stop2.sh"
echo "=== 기동 (base → 보드 리셋 게이트) ==="
timeout 300 sshpass -p <PW> ssh $O jetson@$H "export FASTRTPS_DEFAULT_PROFILES_FILE=\$HOME/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml; bash /tmp/job240_clean.sh 15" 2>&1 | grep -aE "에이전트|컨테이너|세션|시리얼|보드|무발행|wheel_odom|rover/status|gyro|map->odom|자세|중단|단일|프로세스" | head -16
