#!/bin/bash
# BT XML 파일만 배포(src+install), nav2 재기동 없음 + 목표 여유 게이트를 현재 자세에서 시험(mp6 목표 2.2/0 과 후보)
H=${JETSON_HOST:-192.168.0.101}; SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=10"
for f in nav_to_pose_no_spin.xml job377_goalclear.py; do tr -d '\r' < $SPS/$f > /tmp/$f; sshpass -p <PW> scp $O -q /tmp/$f jetson@$H:/tmp/$f || exit 1; done
timeout 120 sshpass -p <PW> ssh $O jetson@$H 'python3 -c "import xml.etree.ElementTree as E;E.parse(\"/tmp/nav_to_pose_no_spin.xml\")" && for d in ~/ros2_ws/src/rover_navigation/config ~/ros2_ws/install/rover_navigation/share/rover_navigation/config; do cp /tmp/nav_to_pose_no_spin.xml $d/; done && echo "BT 파일 배포: TruncatePath $(grep -c TruncatePath ~/ros2_ws/install/rover_navigation/share/rover_navigation/config/nav_to_pose_no_spin.xml) (다음 nav2 기동 반영)"
export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash
echo "현재 로버(목표 부근) 기준 — 시작 프레임과 다르므로 map 좌표로 해석:"; for g in "0.12 -0.21" "0.0 0.0"; do python3 /tmp/job377_goalclear.py $g 2>&1 | grep -a "목표 map"; done'
