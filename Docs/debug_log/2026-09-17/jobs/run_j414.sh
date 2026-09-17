#!/bin/bash
# 출발 자세 교차검증 (주행 없음): 원시 깊이 상자 거리(job369) + 현재 스캔 ↔ mp10·mp11 bag 출발 스캔 ICP(job370)
H=${JETSON_HOST:-172.30.1.8}; SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=10"
for f in job369_boxrange.py job370_scanmatch.py; do tr -d '\r' < $SPS/$f > /tmp/$f; sshpass -p <PW> scp $O -q /tmp/$f jetson@$H:/tmp/$f || exit 1; done
timeout 200 sshpass -p <PW> ssh $O jetson@$H 'export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash
rm -f /tmp/scan_now.npy; python3 /tmp/job369_boxrange.py 2>&1 | grep -avE "^\[|바닥 행"
ls -d /tmp/bag_mp10 /tmp/bag_mp11 2>&1
echo "== ICP vs mp11 출발 (상자 1.153/-0.021)"; python3 /tmp/job370_scanmatch.py /tmp/bag_mp11 /tmp/scan_now.npy 1.153 -0.021 2>&1 | grep -av "^\["
echo "== ICP vs mp10 출발 (상자 1.153/-0.031)"; python3 /tmp/job370_scanmatch.py /tmp/bag_mp10 /tmp/scan_now.npy 1.153 -0.031 2>&1 | grep -av "^\["'
