#!/bin/bash
# 게이트만 (재기동·주행 없음): 상자 감사 + 통로 띠 + 창(3 표본 중앙값)
BXH=${1:-1.09}; BYH=${2:-0.0}
SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=15"
J=jetson@${JETSON_HOST:-192.168.0.101}
A=$(timeout 150 sshpass -p <PW> ssh $O $J "export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; BOX_HINT='$BXH $BYH' python3 /tmp/job248_audit.py 2>&1")
echo "$A" | grep -aE '^상자:|최소폭'
BX=$(echo "$A" | grep -aoE 'x=[0-9.]+' | head -1 | cut -d= -f2); BY=$(echo "$A" | grep -aoE 'y=[-+0-9.]+' | head -1 | cut -d= -f2 | tr -d +)
NB=$(echo "$A" | grep -aE '^  로컬\[' -A1 | grep -aoE '\(\+?[-0-9.]+,[-+0-9.]+\)' | tr -d '()+' | awk -F, '$1>0.3 && $1<1.6 && $2>-0.10 && $2<0.50' | wc -l)
BMS=$(timeout 90 sshpass -p <PW> ssh $O $J "export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; for i in 1 2 3; do python3 /tmp/job315_boxcells.py $BX $BY 2>&1 | grep -av '^\[' | tail -1; sleep 3; done" | tr '\n' ' ')
BM=$(echo $BMS | tr ' ' '\n' | grep -aE '^-?[0-9.]+$' | sort -n | sed -n 2p)
LB=$(echo "$A" | grep -aE '^   1\.[1-3]0 ' | awk '{print $2}' | tr -d '[]' | awk -F'~' -v bm="$BM" '$1+0 > bm+0 {print $2+0}' | sort -n | head -1)
W2=$(awk -v lb="$LB" -v bm="$BM" 'BEGIN{ if (bm=="nan"||bm=="") print "nan"; else printf "%.3f", lb - (bm + 0.195) }')
echo "상자 x=$BX y=$BY | 띠 근거 없는 셀 $NB (≤1) | 상자 셀 3표본 $BMS→ $BM | 창 $W2 m (≥0.20; 좌측 $LB)"
