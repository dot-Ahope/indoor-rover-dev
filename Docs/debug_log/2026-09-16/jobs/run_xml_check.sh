#!/bin/bash
H=${JETSON_HOST:-172.30.1.8}; SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=10"
for f in fastdds_udp_only.xml job359_agentchk.sh job240_clean.sh; do tr -d '\r' < $SPS/$f > /tmp/$f; sshpass -p <PW> scp $O -q /tmp/$f jetson@$H:/tmp/$f || exit 1; done
R=$(sshpass -p <PW> ssh $O jetson@$H 'cp /tmp/fastdds_udp_only.xml ~/ros2_ws/src/rover_bringup/config/; cp /tmp/fastdds_udp_only.xml ~/ros2_ws/install/rover_bringup/share/rover_bringup/config/; echo "whitelist: $(grep -c "<address>" ~/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml)"; bash /tmp/job359_agentchk.sh 2>&1 | grep -aE "CLI"')
echo "$R"
if echo "$R" | grep -a "루프백 CLI" | grep -aq "average rate"; then echo "=== 프로파일 CLI 에서 /wheel_odom 보임 → 기동 진행 ==="; exit 0; else echo "=== 여전히 안 보임 ==="; exit 2; fi
