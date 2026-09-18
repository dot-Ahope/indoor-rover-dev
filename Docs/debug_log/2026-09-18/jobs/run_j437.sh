#!/bin/bash
H=${JETSON_HOST:-192.168.0.101}; NSPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad
O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=10"
for f in job431_odomdrift.py job431b_crab.py; do tr -d '\r' < $NSPS/$f > /tmp/$f; sshpass -p <PW> scp $O -q /tmp/$f jetson@$H:/tmp/ || exit 1; done
A6="/tmp/bag_mp9 1789621954.078 /tmp/bag_mp10 1789622875.413 /tmp/bag_mp11 1789624421.417 /tmp/bag_mp12 1789631920.2186 /tmp/bag_dy1 1789705250.4374 /tmp/bag_dy2 1789705905.1535"
T6="/tmp/bag_mp9 1789621954.078 33.7 /tmp/bag_mp10 1789622875.413 33.1 /tmp/bag_mp11 1789624421.417 33.6 /tmp/bag_mp12 1789631920.2186 31.9 /tmp/bag_dy1 1789705250.4374 32.4 /tmp/bag_dy2 1789705905.1535 33.5"
timeout 1200 sshpass -p <PW> ssh $O jetson@$H "source /opt/ros/humble/setup.bash
echo '######## 보정 분해 (중복 제거, 출발~도착)'; python3 /tmp/job431_odomdrift.py $T6 2>&1 | grep -av 'Opened database' | grep -avE '^통합|해석|회전 Δψ|직선 \|'
echo '######## 게걸음 각 — 보정 전 4 회'; python3 /tmp/job431b_crab.py /tmp/bag_mp9 1789621954.078 /tmp/bag_mp10 1789622875.413 /tmp/bag_mp11 1789624421.417 /tmp/bag_mp12 1789631920.2186 2>&1 | grep -av 'Opened database' | grep -aE '^mp|^통합|heading|곡률'
echo '######## 게걸음 각 — 보정 후 2 회'; python3 /tmp/job431b_crab.py /tmp/bag_dy1 1789705250.4374 /tmp/bag_dy2 1789705905.1535 2>&1 | grep -av 'Opened database' | grep -aE '^dy|^통합|heading|곡률'"
