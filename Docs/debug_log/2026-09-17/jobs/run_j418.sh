#!/bin/bash
H=${JETSON_HOST:-172.30.1.8}; SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=10"
tr -d '\r' < $SPS/job418_mppisrc.sh > /tmp/job418_mppisrc.sh; sshpass -p <PW> scp $O -q /tmp/job418_mppisrc.sh jetson@$H:/tmp/ || exit 1
timeout 60 sshpass -p <PW> ssh $O jetson@$H "bash /tmp/job418_mppisrc.sh"
