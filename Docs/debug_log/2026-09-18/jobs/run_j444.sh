#!/bin/bash
H=${JETSON_HOST:-192.168.0.101}; NSPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad; SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=10"
tr -d '\r' < $NSPS/job444_boxmodel.py > /tmp/job444_boxmodel.py
sshpass -p <PW> scp $O -q /tmp/job444_boxmodel.py $SPS/dy3.csv $SPS/dy4.csv $SPS/dy6.csv jetson@$H:/tmp/ || exit 1
timeout 300 sshpass -p <PW> ssh $O jetson@$H "source /opt/ros/humble/setup.bash; python3 /tmp/job444_boxmodel.py dy3 /tmp/bag_dy3 1789707370.9737 /tmp/dy3.csv 1.151 -0.116 dy4 /tmp/bag_dy4 1789709828.4526 /tmp/dy4.csv 1.161 -0.109 dy6 /tmp/bag_dy6 1789711764.2988 /tmp/dy6.csv 1.143 -0.086 2>&1 | grep -av 'Opened database'"
