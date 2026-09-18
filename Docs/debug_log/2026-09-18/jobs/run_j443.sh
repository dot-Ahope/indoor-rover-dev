#!/bin/bash
H=192.168.0.101; J=jetson@$H; SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=8"
A=$(timeout 150 sshpass -p <PW> ssh $O $J "export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; BOX_HINT='1.163 -0.109' python3 /tmp/job248_audit.py 2>&1")
echo "$A" | grep -aE '^  로컬\[' -A1 | head -8
echo "-- 띠(x 0.3~1.6, y −0.10~+0.50) 안 근거 없는 셀:"; echo "$A" | grep -aE '^  로컬\[' -A1 | grep -aoE '\(\+?[-0-9.]+,[-+0-9.]+\)' | tr -d '()+' | awk -F, '$1>0.3 && $1<1.6 && $2>-0.10 && $2<0.50'
