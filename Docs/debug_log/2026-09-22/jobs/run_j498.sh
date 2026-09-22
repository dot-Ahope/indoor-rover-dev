#!/bin/bash
H=${JETSON_HOST:-192.168.0.101}; NSPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad
O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=10"
ping -c1 -W2 $H >/dev/null 2>&1 && echo "ping $H OK" || { echo "ping $H 실패"; ping -c1 -W2 172.30.1.8 >/dev/null 2>&1 && echo "172.30.1.8 응답(ALOPS 망)"; exit 1; }
tr -d '\r' < $NSPS/job498_state.sh > /tmp/job498_state.sh; sshpass -p <PW> scp $O -q /tmp/job498_state.sh jetson@$H:/tmp/ || exit 1
timeout 90 sshpass -p <PW> ssh $O jetson@$H "bash /tmp/job498_state.sh"
