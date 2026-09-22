#!/bin/bash
# 09-22 N4 회차 bag 분석 러너(PC): 인자 NAME EPOCH(bt_navigator 'Begin navigating' 시각). Jetson /tmp/bag_<NAME> 에 대해 job416(코스트맵 여유)·job446(경로 분해)·job462(bag Hz)·job431b(게걸음)
H=${JETSON_HOST:-192.168.0.101}; NSPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad
O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=10"
N=$1; T0=$2
for f in job416_boxclear.py job446_pathdecomp.py job462_baghz.py job431b_crab.py; do tr -d '\r' < $NSPS/$f > /tmp/$f; sshpass -p <PW> scp $O -q /tmp/$f jetson@$H:/tmp/ || exit 1; done
timeout 900 sshpass -p <PW> ssh $O jetson@$H "source /opt/ros/humble/setup.bash; ls -d /tmp/bag_$N >/dev/null || { echo 'bag 없음'; exit 1; }
echo '######## D. 코스트맵 기준 상자 여유 ($N)'; python3 /tmp/job416_boxclear.py /tmp/bag_$N $T0 2>&1 | grep -av 'Opened database' | grep -aE '^상자|최소|여유|LETHAL|^  *[0-9]+\.[0-9]' | head -40 | cut -c1-170
echo '######## E. 경로 분해 원경로→스무딩→실제 ($N)'; python3 /tmp/job446_pathdecomp.py $N /tmp/bag_$N $T0 2>&1 | grep -av 'Opened database' | tail -14 | cut -c1-170
echo '######## F. bag 발행 주기 ($N)'; python3 /tmp/job462_baghz.py /tmp/bag_$N 2>&1 | grep -av 'Opened database' | tail -14 | cut -c1-150
echo '######## A. 게걸음 각 ($N)'; python3 /tmp/job431b_crab.py /tmp/bag_$N $T0 2>&1 | grep -av 'Opened database' | tail -6 | cut -c1-170"
