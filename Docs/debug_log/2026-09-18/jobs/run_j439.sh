#!/bin/bash
H=${JETSON_HOST:-192.168.0.101}; NSPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad
O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=10"
tr -d '\r' < $NSPS/job439_startcells.py > /tmp/job439_startcells.py; sshpass -p <PW> scp $O -q /tmp/job439_startcells.py jetson@$H:/tmp/ || exit 1
timeout 600 sshpass -p <PW> ssh $O jetson@$H "source /opt/ros/humble/setup.bash; python3 /tmp/job439_startcells.py /tmp/bag_dy3 1789707370.9737 /tmp/bag_dy2 1789705905.1535 2>&1 | grep -av 'Opened database'"
