#!/bin/bash
H=${JETSON_HOST:-172.30.1.8}; SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=10"
for f in job410_mppi_sim_lag.py job411_tempsim.sh; do tr -d '\r' < $SPS/$f > /tmp/$f; sshpass -p <PW> scp $O -q /tmp/$f jetson@$H:/tmp/$f || exit 1; done
timeout 30 sshpass -p <PW> ssh $O jetson@$H "rm -f /tmp/tempsim.log; setsid nohup bash /tmp/job411_tempsim.sh > /tmp/tempsim.log 2>&1 & echo started \$(date +%T)"
bash $SPS/run_waitsim.sh /tmp/tempsim.log 1500
