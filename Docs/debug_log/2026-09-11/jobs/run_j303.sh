#!/bin/bash
SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
OPT="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=15"
J=jetson@192.168.0.101
ping -w 60 -c 1 192.168.0.101 >/dev/null 2>&1 && echo "핑 OK" || { echo "핑 실패"; exit 1; }
for i in 1 2 3; do sshpass -p <PW> ssh $OPT $J "echo ssh OK; uptime | cut -d, -f3-" && break; sleep 10; done
sshpass -p <PW> scp $OPT -q $J:/tmp/v5.csv $SPS/v5.csv && echo "v5.csv 회수 OK"
tr -d '\r' < $SPS/job303_bagstall.py > /tmp/job303.py
sshpass -p <PW> scp $OPT -q /tmp/job303.py $J:/tmp/job303_bagstall.py || exit 1
echo "=== v5 정체 순간 (첫 충돌 감지) ==="
timeout 300 sshpass -p <PW> ssh $OPT $J "source /opt/ros/humble/setup.bash; python3 /tmp/job303_bagstall.py /tmp/bag_v5 1789116145.96 2>&1 | grep -av 'Opened database'"
echo "=== v5 nav2.log 충돌·복구 시각 목록 ==="
sshpass -p <PW> ssh $OPT $J "grep -aoE '^\[[a-z_]+-[0-9]+\] \[(WARN|ERROR|INFO)\] \[[0-9.]+\] \[(controller_server|behavior_server|bt_navigator)\]: .{0,90}' /tmp/nav2.log | grep -aE 'collision|Collision|Running|succeeded|failed|ABORT|Aborting|Goal' | grep -a 178911614 | head -40"
