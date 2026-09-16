#!/bin/bash
# depth_relay.py + camera.launch.py 를 src·install 에 배포 (반영은 다음 sensors 재기동)
SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
OPT="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=15"
J=jetson@${JETSON_HOST:-192.168.0.101}
for f in depth_relay.py camera.launch.py; do tr -d '\r' < $SPS/$f > /tmp/$f; sshpass -p <PW> scp $OPT -q /tmp/$f $J:/tmp/$f || exit 1; done
sshpass -p <PW> ssh $OPT $J 'python3 -c "import ast;ast.parse(open(\"/tmp/depth_relay.py\").read())" && cp /tmp/depth_relay.py ~/ros2_ws/src/rover_bringup/scripts/ && cp /tmp/depth_relay.py ~/ros2_ws/install/rover_bringup/lib/rover_bringup/depth_relay.py && chmod +x ~/ros2_ws/install/rover_bringup/lib/rover_bringup/depth_relay.py && cp /tmp/camera.launch.py ~/ros2_ws/src/rover_bringup/launch/ && cp /tmp/camera.launch.py ~/ros2_ws/install/rover_bringup/share/rover_bringup/launch/ && grep -c "array.array" ~/ros2_ws/install/rover_bringup/lib/rover_bringup/depth_relay.py && grep -o "max_range.: [0-9.]*" ~/ros2_ws/install/rover_bringup/share/rover_bringup/launch/camera.launch.py && echo "relay 배포 OK (다음 sensors 재기동 반영)"'
