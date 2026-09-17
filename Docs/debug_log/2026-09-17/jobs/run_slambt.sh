#!/bin/bash
H=${JETSON_HOST:-192.168.0.101}; SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=10 -o ServerAliveInterval=5"
sed 's/__PW__/<PW>/' $SPS/job387_slambt.sh | tr -d '\r' > /tmp/job387_slambt.sh
sshpass -p <PW> scp $O -q /tmp/job387_slambt.sh jetson@$H:/tmp/job387_slambt.sh || exit 1
timeout 200 sshpass -p <PW> ssh $O jetson@$H "bash /tmp/job387_slambt.sh; rm -f /tmp/job387_slambt.sh"
rm -f /tmp/job387_slambt.sh
sshpass -p <PW> scp $O -q jetson@$H:/tmp/slam_bt.txt $SPS/slam_bt.txt && echo "회수 $(wc -l < $SPS/slam_bt.txt) 줄"
