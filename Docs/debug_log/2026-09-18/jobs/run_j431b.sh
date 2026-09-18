#!/bin/bash
H=${JETSON_HOST:-192.168.0.101}; NSPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad
O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=10"
tr -d '\r' < $NSPS/job431b_crab.py > /tmp/job431b_crab.py; sshpass -p <PW> scp $O -q /tmp/job431b_crab.py jetson@$H:/tmp/ || exit 1
timeout 600 sshpass -p <PW> ssh $O jetson@$H "source /opt/ros/humble/setup.bash; python3 /tmp/job431b_crab.py /tmp/bag_mp9 1789621954.078 /tmp/bag_mp10 1789622875.413 /tmp/bag_mp11 1789624421.417 /tmp/bag_mp12 1789631920.2186 2>&1 | grep -av 'Opened database'"
