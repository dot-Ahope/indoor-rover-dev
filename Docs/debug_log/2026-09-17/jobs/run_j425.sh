#!/bin/bash
H=${JETSON_HOST:-172.30.1.8}; SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=10"
tr -d '\r' < $SPS/job425_detour.py > /tmp/job425_detour.py; sshpass -p <PW> scp $O -q /tmp/job425_detour.py jetson@$H:/tmp/ || exit 1
printf '%s\n' 'source /opt/ros/humble/setup.bash' 'python3 /tmp/job425_detour.py /tmp/bag_mp12 1789631920.2186 1' 'python3 /tmp/job425_detour.py /tmp/bag_mp11 1789624421.417' 'python3 /tmp/job425_detour.py /tmp/bag_mp9 1789621954.078' 'echo END425' > /tmp/job425_run.sh
sshpass -p <PW> scp $O -q /tmp/job425_run.sh jetson@$H:/tmp/ || exit 1
timeout 30 sshpass -p <PW> ssh $O jetson@$H "rm -f /tmp/det425.log; setsid nohup bash /tmp/job425_run.sh > /tmp/det425.log 2>&1 & echo started"
for i in $(seq 1 60); do
  sleep 10
  n=$(timeout 15 sshpass -p <PW> ssh $O jetson@$H "grep -ac END425 /tmp/det425.log" 2>/dev/null)
  [ "$n" = "1" ] && break
done
timeout 20 sshpass -p <PW> ssh $O jetson@$H "grep -av 'Opened database' /tmp/det425.log"
