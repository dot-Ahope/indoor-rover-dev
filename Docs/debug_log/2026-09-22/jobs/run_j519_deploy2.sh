#!/bin/bash
# N6-1 배포(PC, 2026-09-22): nav2_params.yaml(전역 nvblox_layer 블록)·navigation.launch.py(전역 plugins 전환)·depth_relay.py(구독자 없으면 생략) → Jetson 소스 → colcon(rover_navigation, rover_bringup). 재기동은 따로(run_mp9prep).
H=${JETSON_HOST:-192.168.0.101}; NSPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad
O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=10"
SRC=$NSPS/n61_src; mkdir -p /tmp/x519
for f in nav2_params.yaml navigation.launch.py depth_relay.py; do tr -d '\r' < $SRC/$f > /tmp/x519/$f || exit 1; done
python3 -c "import yaml; yaml.safe_load(open('/tmp/x519/nav2_params.yaml'))" && echo "yaml 파싱 OK" || exit 1
sshpass -p <PW> scp $O -q /tmp/x519/nav2_params.yaml jetson@$H:~/ros2_ws/src/rover_navigation/config/ && sshpass -p <PW> scp $O -q /tmp/x519/navigation.launch.py jetson@$H:~/ros2_ws/src/rover_navigation/launch/ && sshpass -p <PW> scp $O -q /tmp/x519/depth_relay.py jetson@$H:~/ros2_ws/src/rover_bringup/scripts/ || { echo "전송 실패"; exit 1; }
tr -d '\r' < $NSPS/job489_gridcmp.py > /tmp/job489_gridcmp.py; sshpass -p <PW> scp $O -q /tmp/job489_gridcmp.py jetson@$H:/tmp/
timeout 300 sshpass -p <PW> ssh $O jetson@$H "source /opt/ros/humble/setup.bash; cd ~/ros2_ws; T0=\$(date +%s); colcon build --symlink-install --packages-select rover_navigation rover_bringup 2>&1 | grep -aE 'Finished|Failed|error' | tail -4; echo \"빌드 \$(( \$(date +%s) - T0 )) s\"; md5sum ~/ros2_ws/install/rover_navigation/share/rover_navigation/config/nav2_params.yaml ~/ros2_ws/install/rover_bringup/lib/rover_bringup/depth_relay.py 2>/dev/null | cut -c1-12,33- ; grep -c nvblox_layer ~/ros2_ws/install/rover_navigation/share/rover_navigation/config/nav2_params.yaml"
