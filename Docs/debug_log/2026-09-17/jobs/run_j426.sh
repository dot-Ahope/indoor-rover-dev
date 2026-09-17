#!/bin/bash
H=${JETSON_HOST:-172.30.1.8}; SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=10"
tr -d '\r' < $SPS/job426_boxframes.py > /tmp/job426_boxframes.py; sshpass -p <PW> scp $O -q /tmp/job426_boxframes.py jetson@$H:/tmp/ || exit 1
timeout 500 sshpass -p <PW> ssh $O jetson@$H "source /opt/ros/humble/setup.bash; for a in 'mp12 1789631920.2186' 'mp11 1789624421.417' 'mp9 1789621954.078'; do set -- \$a; python3 /tmp/job426_boxframes.py /tmp/bag_\$1 \$2 2>&1 | grep -av 'Opened database'; done"
