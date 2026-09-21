#!/bin/bash
# 인자: stvl|nvblox BX BY
H=${JETSON_HOST:-192.168.0.101}; NSPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad; SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=10"
tr -d '\r' < $NSPS/job488_layer_ab.sh > /tmp/job488_layer_ab.sh; sshpass -p <PW> scp $O -q /tmp/job488_layer_ab.sh jetson@$H:/tmp/ || exit 1
for f in job248_audit.py job315_boxcells.py; do tr -d '\r' < $SPS/$f > /tmp/$f; sshpass -p <PW> scp $O -q /tmp/$f jetson@$H:/tmp/ || exit 1; done
timeout 500 sshpass -p <PW> ssh $O jetson@$H "export TERM=xterm; bash /tmp/job488_layer_ab.sh $1 $2 $3 2>&1"
