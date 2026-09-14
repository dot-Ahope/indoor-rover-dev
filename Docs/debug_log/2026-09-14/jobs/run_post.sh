#!/bin/bash
# 주행 직후: bag·csv 회수(재부팅 전 필수) + 차체 고정점 판정(job310)
NAME=${1:-inf1}
SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
OPT="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=15"
J=jetson@192.168.0.101
mkdir -p $SPS/bags
sshpass -p <PW> ssh $OPT $J "cd /tmp && tar czf /tmp/bag_$NAME.tgz bag_$NAME bag_$NAME.log 2>/dev/null; ls -la /tmp/bag_$NAME.tgz /tmp/$NAME.csv 2>&1 | awk '{print \$5, \$9}'"
sshpass -p <PW> scp $OPT -q $J:/tmp/bag_$NAME.tgz $SPS/bags/ && echo "bag 회수 OK: $(stat -c %s $SPS/bags/bag_$NAME.tgz) B"
sshpass -p <PW> scp $OPT -q $J:/tmp/$NAME.csv $SPS/$NAME.csv && echo "csv 회수 OK"
tr -d '\r' < $SPS/job310_bodyfixed.py > /tmp/job310.py; sshpass -p <PW> scp $OPT -q /tmp/job310.py $J:/tmp/job310_bodyfixed.py
echo "=== 차체 고정점 판정 (bag_$NAME) ==="
timeout 300 sshpass -p <PW> ssh $OPT $J "source /opt/ros/humble/setup.bash; python3 /tmp/job310_bodyfixed.py /tmp/bag_$NAME 2>&1 | grep -av 'Opened database'"
