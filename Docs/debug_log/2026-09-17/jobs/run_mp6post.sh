#!/bin/bash
H=${JETSON_HOST:-192.168.0.101}; SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=10 -o ServerAliveInterval=5"
tr -d '\r' < $SPS/job373_mp6post.sh > /tmp/job373_mp6post.sh; sshpass -p <PW> scp $O -q /tmp/job373_mp6post.sh jetson@$H:/tmp/ || exit 1
timeout 200 sshpass -p <PW> ssh $O jetson@$H "bash /tmp/job373_mp6post.sh"
sshpass -p <PW> scp $O -q jetson@$H:/tmp/bag_mp6.tgz $SPS/bags/bag_mp6.tgz && echo "bag 회수 OK $(stat -c %s $SPS/bags/bag_mp6.tgz)"
sshpass -p <PW> scp $O -q jetson@$H:/tmp/drive_mp6.log $SPS/drive_mp6_remote.log && echo "drive log OK"
