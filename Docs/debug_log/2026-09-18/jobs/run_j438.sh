#!/bin/bash
H=${JETSON_HOST:-192.168.0.101}; NSPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad
O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=10"
tr -d '\r' < $NSPS/job438_tfgaps.py > /tmp/job438_tfgaps.py; sshpass -p <PW> scp $O -q /tmp/job438_tfgaps.py jetson@$H:/tmp/ || exit 1
timeout 900 sshpass -p <PW> ssh $O jetson@$H "source /opt/ros/humble/setup.bash; python3 /tmp/job438_tfgaps.py /tmp/bag_mp9 1789621954.078 33.7 25.45 -- /tmp/bag_mp10 1789622875.413 33.1 18.57 -- /tmp/bag_mp11 1789624421.417 33.6 -- /tmp/bag_mp12 1789631920.2186 31.9 19.16 -- /tmp/bag_dy1 1789705250.4374 32.4 -- /tmp/bag_dy2 1789705905.1535 33.5 2>&1 | grep -av 'Opened database'"
