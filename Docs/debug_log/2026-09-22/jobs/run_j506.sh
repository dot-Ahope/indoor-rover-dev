#!/bin/bash
H=${JETSON_HOST:-192.168.0.101}; NSPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad
O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=10"
for f in job506_decay.sh job506_decay.py nvblox_n0_t2d99.yaml; do tr -d '\r' < $NSPS/$f > /tmp/$f; sshpass -p <PW> scp $O -q /tmp/$f jetson@$H:/tmp/ || exit 1; done
timeout 400 sshpass -p <PW> ssh $O jetson@$H "export TERM=xterm; bash /tmp/job506_decay.sh $1 $2 $3 $4 ${5:-80}"
