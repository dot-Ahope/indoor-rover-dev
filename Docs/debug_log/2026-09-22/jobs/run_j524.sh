#!/bin/bash
# 재탐침만: job522(목표 부근) + 게이트 J·K·L + 목표 여유(job377 D LAT). 인자: BX BY
H=${JETSON_HOST:-192.168.0.101}; NSPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad
O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=10"
BX=${1:-1.145}; BY=${2:--0.068}
tr -d '\r' < $NSPS/job522_goalprobe.py > /tmp/job522_goalprobe.py; sshpass -p <PW> scp $O -q /tmp/job522_goalprobe.py jetson@$H:/tmp/ || exit 1
timeout 200 sshpass -p <PW> ssh $O jetson@$H "export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo '## 목표 부근 탐침'; python3 /tmp/job522_goalprobe.py 2>&1 | grep -av '^\['
echo '## 게이트 J·K·L'; bash /tmp/job505_modeN_gate.sh node $BX $BY 2>&1 | grep -aE '^[JKL] |=='
echo '## 목표 여유(job377 2.0 0.0)'; timeout 60 python3 /tmp/job377_goalclear.py 2.0 0.0 2>&1 | grep -av '^\[' | tail -2"
