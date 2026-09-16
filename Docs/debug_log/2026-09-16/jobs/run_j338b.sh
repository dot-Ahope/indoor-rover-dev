#!/bin/bash
# job338 재실행: mp2 + (있으면) bk1 업로드 후 분석
SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
OPT="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=15"
J=jetson@${JETSON_HOST:-192.168.0.101}
tr -d '\r' < $SPS/job338_ghost_decay.py > /tmp/job338_ghost_decay.py; sshpass -p <PW> scp $OPT -q /tmp/job338_ghost_decay.py $J:/tmp/ || exit 1
if [ -f $SPS/bags/bag_bk1.tgz ]; then sshpass -p <PW> scp $OPT -q $SPS/bags/bag_bk1.tgz $J:/tmp/bag_bk1.tgz && echo "bk1 업로드"; fi
timeout 900 sshpass -p <PW> ssh $OPT $J "source /opt/ros/humble/setup.bash; cd /tmp; [ -f bag_bk1.tgz ] && [ ! -d bag_bk1 ] && tar xzf bag_bk1.tgz 2>/dev/null; ls -d /tmp/bag_bk1* 2>/dev/null | head -3; for b in mp2:1.187:0.074 bk1:1.19:0.0; do IFS=: read n x y <<< \"\$b\"; [ -d /tmp/bag_\$n ] || { echo \"bag_\$n 없음\"; continue; }; echo \"################ bag_\$n\"; python3 /tmp/job338_ghost_decay.py /tmp/bag_\$n \$x \$y 60 120 90 180 2>&1 | grep -av 'Opened database'; done"
