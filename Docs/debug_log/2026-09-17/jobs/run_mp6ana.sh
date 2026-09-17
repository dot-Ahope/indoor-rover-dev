#!/bin/bash
H=${JETSON_HOST:-192.168.0.101}; SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=10 -o ServerAliveInterval=5"
for f in job327_mp2why.py job345_traj.py job355_mppi_sim.py job374_mp6ana.sh job375_goalsim.sh job376_goalview.sh; do tr -d '\r' < $SPS/$f > /tmp/$f; sshpass -p <PW> scp $O -q /tmp/$f jetson@$H:/tmp/$f || { echo "scp 실패 $f"; exit 1; }; done
timeout 280 sshpass -p <PW> ssh $O jetson@$H "bash /tmp/${1:-job374_mp6ana.sh}"
