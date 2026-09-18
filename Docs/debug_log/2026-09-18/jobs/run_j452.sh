#!/bin/bash
H=${JETSON_HOST:-192.168.0.101}; NSPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad
O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=10"
for f in job452_mppi_sim_cc.py job452_run.sh; do tr -d '\r' < $NSPS/$f > /tmp/$f; sshpass -p <PW> scp $O -q /tmp/$f jetson@$H:/tmp/ || exit 1; done
timeout 2400 sshpass -p <PW> ssh $O jetson@$H "ls -d /tmp/bag_dy2 /tmp/bag_dy4 /tmp/bag_dy6 >/dev/null || exit 1; nohup bash /tmp/job452_run.sh > /tmp/j452.log 2>&1 & echo started"
