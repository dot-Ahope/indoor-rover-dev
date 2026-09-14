#!/bin/bash
SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
OPT="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=15"
J=jetson@192.168.0.101
echo "=== RealSense threshold/decimation 파라미터 이름 ==="
sshpass -p <PW> ssh $OPT $J "source /opt/ros/humble/setup.bash; timeout 15 ros2 param list /camera/camera 2>/dev/null | grep -aiE 'threshold|decimation|min_dist|max_dist' | tr '\n' ' '; echo"
bash $SPS/run_inf1.sh inf2 2.0 1.13 -0.04 0.06
