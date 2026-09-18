#!/bin/bash
H=${JETSON_HOST:-192.168.0.101}; NSPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad
O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=10"
tr -d '\r' < $NSPS/job446_pathdecomp.py > /tmp/job446_pathdecomp.py; sshpass -p <PW> scp $O -q /tmp/job446_pathdecomp.py jetson@$H:/tmp/ || exit 1
timeout 1500 sshpass -p <PW> ssh $O jetson@$H "source /opt/ros/humble/setup.bash; ls -d /tmp/bag_dy1 /tmp/bag_dy2 /tmp/bag_dy3 /tmp/bag_dy4 /tmp/bag_dy5 /tmp/bag_dy6 >/dev/null || exit 1; python3 /tmp/job446_pathdecomp.py dy1 /tmp/bag_dy1 1789705250.4374 dy2 /tmp/bag_dy2 1789705905.1535 dy3 /tmp/bag_dy3 1789707370.9737 dy4 /tmp/bag_dy4 1789709828.4526 dy5 /tmp/bag_dy5 1789710658.6025 dy6 /tmp/bag_dy6 1789711764.2988 2>&1 | grep -av 'Opened database'"
