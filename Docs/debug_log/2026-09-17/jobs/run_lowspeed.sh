#!/bin/bash
H=${JETSON_HOST:-172.30.1.8}; SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=10 -o ServerAliveInterval=5"
tr -d '\r' < $SPS/job397_lowspeed.py > /tmp/job397_lowspeed.py; sshpass -p <PW> scp $O -q /tmp/job397_lowspeed.py jetson@$H:/tmp/ || exit 1
timeout 30 sshpass -p <PW> ssh $O jetson@$H "export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; rm -f /tmp/lowspeed.log; setsid nohup python3 /tmp/job397_lowspeed.py 3.0 > /tmp/lowspeed.log 2>&1 & echo started \$(date +%T)"
T0=$(date +%s)
while [ $(( $(date +%s) - T0 )) -lt 150 ]; do
  sleep 5
  OUT=$(timeout 15 sshpass -p <PW> ssh $O jetson@$H "cat /tmp/lowspeed.log; pgrep -fc job397_lowspeed" 2>/dev/null) || { echo "  (ssh 재시도 $(date +%T))"; continue; }
  RUN=$(echo "$OUT" | tail -1)
  if [ "$RUN" = "0" ]; then echo "$OUT" | sed '$d' | grep -av '^\['; echo "=== 끝 $(date +%T) ==="; exit 0; fi
done
echo "=== 150 s 초과 — 로그 ==="; timeout 15 sshpass -p <PW> ssh $O jetson@$H "cat /tmp/lowspeed.log"
