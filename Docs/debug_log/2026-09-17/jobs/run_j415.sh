#!/bin/bash
H=${JETSON_HOST:-172.30.1.8}; SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=10"
tr -d '\r' < $SPS/job415_sectors.py > /tmp/job415_sectors.py; sshpass -p <PW> scp $O -q /tmp/job415_sectors.py jetson@$H:/tmp/ || exit 1
timeout 120 sshpass -p <PW> ssh $O jetson@$H 'pkill -f "[j]ob370_scanmatch"; sleep 1; echo "job370 남은 프로세스: $(pgrep -fc "[j]ob370_scanmatch")"; source /opt/ros/humble/setup.bash
for b in mp10 mp11; do echo "== vs $b 출발"; python3 /tmp/job415_sectors.py /tmp/bag_$b /tmp/scan_now.npy 2>&1 | grep -av "^\["; done'
