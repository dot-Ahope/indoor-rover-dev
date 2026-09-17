#!/bin/bash
H=${JETSON_HOST:-192.168.0.101}; SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=10 -o ServerAliveInterval=5"
for f in job369_boxrange.py job370_scanmatch.py; do tr -d '\r' < $SPS/$f > /tmp/$f; sshpass -p <PW> scp $O -q /tmp/$f jetson@$H:/tmp/$f || exit 1; done
echo "=== (1)(2)(3) 깊이·구름·스캔 ==="
timeout 120 sshpass -p <PW> ssh $O jetson@$H "export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; python3 /tmp/job369_boxrange.py 2>&1 | grep -av '^\['; echo -n '  emitter: '; timeout 6 ros2 param get /camera/camera depth_module.emitter_enabled 2>&1 | tail -1; echo -n '  depth profile: '; timeout 6 ros2 param get /camera/camera depth_module.depth_profile 2>&1 | tail -1"
echo "=== 어제 mp5 bag 업로드·정합 ==="
sshpass -p <PW> scp $O -q $SPS/bags/bag_mp5.tgz jetson@$H:/tmp/bag_mp5.tgz || { echo "bag 업로드 실패"; exit 1; }
timeout 300 sshpass -p <PW> ssh $O jetson@$H "source /opt/ros/humble/setup.bash; cd /tmp && rm -rf bag_mp5 && tar xzf bag_mp5.tgz && python3 /tmp/job370_scanmatch.py /tmp/bag_mp5 /tmp/scan_now.npy 1.174 -0.013 2>&1 | grep -av 'Opened database'"
