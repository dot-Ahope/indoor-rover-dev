#!/bin/bash
SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
OPT="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=15"
J=jetson@192.168.0.101
tr -d '\r' < $SPS/nav2_params.yaml > /tmp/nav2_params.yaml
sshpass -p <PW> scp $OPT -q /tmp/nav2_params.yaml $J:/tmp/nav2_params.yaml || exit 1
sshpass -p <PW> ssh $OPT $J "python3 -c \"import yaml; yaml.safe_load(open('/tmp/nav2_params.yaml'))\" && cp /tmp/nav2_params.yaml ~/ros2_ws/src/rover_navigation/config/nav2_params.yaml && cp /tmp/nav2_params.yaml ~/ros2_ws/install/rover_navigation/share/rover_navigation/config/nav2_params.yaml && grep -nE '^\s+voxel_decay:' ~/ros2_ws/install/rover_navigation/share/rover_navigation/config/nav2_params.yaml && echo '배포 OK (src+install; 재기동 시 반영)'"
