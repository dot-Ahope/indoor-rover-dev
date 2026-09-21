#!/bin/bash
H=${JETSON_HOST:-192.168.0.101}; NSPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad
O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=10"
for f in job416_boxclear.py job426_boxframes.py job431_odomdrift.py job431b_crab.py; do tr -d '\r' < $NSPS/$f > /tmp/$f; sshpass -p <PW> scp $O -q /tmp/$f jetson@$H:/tmp/ || exit 1; done
timeout 900 sshpass -p <PW> ssh $O jetson@$H "source /opt/ros/humble/setup.bash; ls -d /tmp/bag_cc4 >/dev/null || exit 1
echo '######## A. 게걸음 각 (cc4)'; python3 /tmp/job431b_crab.py /tmp/bag_cc4 1789969373.3326 2>&1 | grep -av 'Opened database'
echo '######## B. SLAM 보정 분해 (cc4)'; python3 /tmp/job431_odomdrift.py /tmp/bag_cc4 1789969373.3326 2>&1 | grep -av 'Opened database'
echo '######## C. 로컬 vs 전역 상자 (cc4)'; python3 /tmp/job426_boxframes.py /tmp/bag_cc4 1789969373.3326 2>&1 | grep -av 'Opened database'
echo '######## D. 코스트맵 기준 상자 여유 (cc4)'; python3 /tmp/job416_boxclear.py /tmp/bag_cc4 1789969373.3326 2>&1 | grep -av 'Opened database' | grep -aE '^상자 LETHAL|^ +(1[4-9]|2[0-9])\.[0-9] \|'"
