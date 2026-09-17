#!/bin/bash
H=${JETSON_HOST:-192.168.0.101}; SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=10"
echo "=== 1. 재기동 ==="; bash $SPS/${RUNJ:-run_j.sh} job240_clean.sh 15 2>&1 | grep -aE '에이전트|세션|무발행|wheel_odom|gyro|map->odom|자세|중단'
for f in job397_lowspeed.py job400_rotclear.py job386_slamalive.py job314_relay_orphan.sh; do tr -d '\r' < $SPS/$f > /tmp/$f; sshpass -p <PW> scp $O -q /tmp/$f jetson@$H:/tmp/$f || exit 1; done
echo "=== 2. 릴레이 ==="; timeout 60 sshpass -p <PW> ssh $O jetson@$H "bash /tmp/job314_relay_orphan.sh" 2>&1 | grep -aE "남은 릴레이"
echo "=== 3. SLAM·보드·회전 여유 ==="
timeout 120 sshpass -p <PW> ssh $O jetson@$H "export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; python3 /tmp/job386_slamalive.py 2>&1 | grep -av '^\['; printf 'status: '; timeout 5 ros2 topic echo /rover/status --once 2>/dev/null | grep -aE 'value:' | head -2 | tr -s ' ' | tr '\n' ' '; echo; python3 /tmp/job400_rotclear.py 2>&1 | grep -av '^\['; printf 'battery: '; timeout 6 ros2 topic echo /battery --once 2>/dev/null | grep -aoE 'voltage: [0-9.]+'"
