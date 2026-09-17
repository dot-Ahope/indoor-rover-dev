#!/bin/bash
H=${JETSON_HOST:-192.168.0.101}; SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=10 -o ServerAliveInterval=5"
N=${1:-mp7}
tr -d '\r' < $SPS/job379_navevents.sh > /tmp/job379_navevents.sh; sshpass -p <PW> scp $O -q /tmp/job379_navevents.sh jetson@$H:/tmp/ || exit 1
timeout 200 sshpass -p <PW> ssh $O jetson@$H "bash /tmp/job379_navevents.sh $N"
sshpass -p <PW> scp $O -q jetson@$H:/tmp/bag_$N.tgz $SPS/bags/bag_$N.tgz && echo "bag 회수 OK $(stat -c %s $SPS/bags/bag_$N.tgz)"
sshpass -p <PW> scp $O -q jetson@$H:/tmp/drive_$N.log $SPS/drive_${N}_remote.log && echo "drive log OK"
sshpass -p <PW> scp $O -q jetson@$H:/tmp/$N.csv $SPS/$N.csv && echo "csv OK"
