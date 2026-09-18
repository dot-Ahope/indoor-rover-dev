#!/bin/bash
H=${JETSON_HOST:-192.168.0.101}; NSPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad
O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=10"
for f in job428b_now.sh job428_wifi_dfs.sh; do tr -d '\r' < $NSPS/$f > /tmp/$f; sshpass -p <PW> scp $O -q /tmp/$f jetson@$H:/tmp/ || exit 1; done
timeout 60 sshpass -p <PW> ssh $O jetson@$H "bash /tmp/job428b_now.sh"
echo "################ job428"
timeout 400 sshpass -p <PW> ssh $O jetson@$H "bash /tmp/job428_wifi_dfs.sh"
