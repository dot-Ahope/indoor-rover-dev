#!/bin/bash
H=${JETSON_HOST:-192.168.0.101}; NSPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad
O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=10"
tr -d '\r' < $NSPS/job434_base.sh > /tmp/job434_base.sh; sshpass -p <PW> scp $O -q /tmp/job434_base.sh jetson@$H:/tmp/ || exit 1
timeout 120 sshpass -p <PW> ssh $O jetson@$H "bash /tmp/job434_base.sh 2>&1"
