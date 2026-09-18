#!/bin/bash
H=${JETSON_HOST:-192.168.0.101}; NSPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad
O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=10"
tr -d '\r' < $NSPS/job431c_bigcorr.py > /tmp/job431c_bigcorr.py; sshpass -p <PW> scp $O -q /tmp/job431c_bigcorr.py jetson@$H:/tmp/ || exit 1
timeout 900 sshpass -p <PW> ssh $O jetson@$H "source /opt/ros/humble/setup.bash; python3 /tmp/job431c_bigcorr.py /tmp/bag_mp12 1789631920.2186 31.9 /tmp/bag_dy1 1789705250.4374 32.4 /tmp/bag_dy2 1789705905.1535 33.5 2>&1 | grep -av 'Opened database'"
