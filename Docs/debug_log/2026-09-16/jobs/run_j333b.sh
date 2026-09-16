#!/bin/bash
# job333 을 raw(백그라운드)·filtered(전경) 두 토픽으로 동시에 DUR 초 실행, 사건(y ≥ EVENT_Y) 기록
SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
OPT="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=15"
J=jetson@${JETSON_HOST:-192.168.0.101}
tr -d '\r' < $SPS/job333_voxstat.py > /tmp/job333_voxstat.py; sshpass -p <PW> scp $OPT -q /tmp/job333_voxstat.py $J:/tmp/ || exit 1
DUR=${5:-180}
timeout $((DUR+90)) sshpass -p <PW> ssh $OPT $J "source /opt/ros/humble/setup.bash; EVENT_Y=${6:-0.20} python3 /tmp/job333_voxstat.py $1 $2 $3 $4 $DUR /camera/camera/depth/color/points > /tmp/j333_raw.txt 2>&1 & EVENT_Y=${6:-0.20} python3 /tmp/job333_voxstat.py $1 $2 $3 $4 $DUR /camera/depth/points_filtered > /tmp/j333_filt.txt 2>&1; wait; echo '##### RAW'; grep -av '^\[' /tmp/j333_raw.txt | sed -n '1,3p;/점≥1/,/복셀≥2/p;/사건/,\$p'; echo '##### FILTERED'; grep -av '^\[' /tmp/j333_filt.txt | sed -n '1,3p;/점≥1/,/복셀≥2/p;/복셀≥3/,/최대/p;/사건/,\$p'"
