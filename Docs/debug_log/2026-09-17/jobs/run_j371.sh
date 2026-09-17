#!/bin/bash
H=${JETSON_HOST:-192.168.0.101}; SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=10 -o ServerAliveInterval=5"
for f in job248_audit.py job371_costbox.py; do tr -d '\r' < $SPS/$f > /tmp/$f; sshpass -p <PW> scp $O -q /tmp/$f jetson@$H:/tmp/$f || exit 1; done
timeout 200 sshpass -p <PW> ssh $O jetson@$H "export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; echo '=== 코스트맵 비교 ==='; python3 /tmp/job371_costbox.py /tmp/bag_mp5 2>&1 | grep -av 'Opened database'; echo '=== 고친 감사 ==='; BOX_HINT='1.35 -0.05' python3 /tmp/job248_audit.py 2>&1 | grep -aE 'x 분할|낮은 클러스터|^상자:'"
echo "=== 게이트 ==="; JETSON_HOST=$H bash $SPS/run_gate.sh 1.35 -0.05
