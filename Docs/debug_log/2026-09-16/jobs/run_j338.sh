#!/bin/bash
SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
OPT="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=15"
J=jetson@${JETSON_HOST:-192.168.0.101}
tr -d '\r' < $SPS/job338_ghost_decay.py > /tmp/job338_ghost_decay.py; sshpass -p <PW> scp $OPT -q /tmp/job338_ghost_decay.py $J:/tmp/ || exit 1
timeout 900 sshpass -p <PW> ssh $OPT $J "source /opt/ros/humble/setup.bash; for b in mp2:1.187:0.074 mp3:1.161:0.049; do IFS=: read n x y <<< \"\$b\"; echo \"################ bag_\$n\"; python3 /tmp/job338_ghost_decay.py /tmp/bag_\$n \$x \$y 60 120 90 180 2>&1 | grep -av 'Opened database'; done"
