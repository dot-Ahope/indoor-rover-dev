#!/bin/bash
H=${JETSON_HOST:-192.168.0.101}; SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=10 -o ServerAliveInterval=5"
sed 's/__PW__/<PW>/' $SPS/job388_pm25.sh | tr -d '\r' > /tmp/job388_pm25.sh
sshpass -p <PW> scp $O -q /tmp/job388_pm25.sh jetson@$H:/tmp/job388_pm25.sh || exit 1
timeout 120 sshpass -p <PW> ssh $O jetson@$H "bash /tmp/job388_pm25.sh; rm -f /tmp/job388_pm25.sh"
rm -f /tmp/job388_pm25.sh
