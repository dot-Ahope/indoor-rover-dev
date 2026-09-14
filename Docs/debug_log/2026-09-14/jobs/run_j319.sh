#!/bin/bash
SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
OPT="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=15"
J=jetson@192.168.0.101
tr -d '\r' < $SPS/job319_gwobble2.py > /tmp/job319.py; sshpass -p <PW> scp $OPT -q /tmp/job319.py $J:/tmp/job319_gwobble2.py || exit 1
timeout 420 sshpass -p <PW> ssh $OPT $J "source /opt/ros/humble/setup.bash; echo \"시작 카운터: slam 폐기 \$(grep -ac 'discard\|Discard\|rejected' /tmp/slam.log 2>/dev/null), EKF 위반 \$(grep -ac 'violat' /tmp/sensors.log 2>/dev/null)\"; python3 -u /tmp/job319_gwobble2.py ${1:-1.036} ${2:--0.005} ${3:-300} 10 2>&1 | grep -av '^\[INFO\]'; echo \"끝 카운터: slam 폐기 \$(grep -ac 'discard\|Discard\|rejected' /tmp/slam.log 2>/dev/null), EKF 위반 \$(grep -ac 'violat' /tmp/sensors.log 2>/dev/null)\"; echo '--- slam.log 최근 5줄 ---'; tail -5 /tmp/slam.log | cut -c1-160"
