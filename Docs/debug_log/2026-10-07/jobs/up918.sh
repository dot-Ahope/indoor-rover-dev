#!/bin/bash
# 10-07 §6: nav2_params(transform_tolerance 0.5) 배포·빌드
O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR"; J=jetson@${JETSON_HOST:-172.30.1.8}
tr -d '\r' < /mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad/r3src/nav2_params.yaml > /tmp/nav2_params.yaml
sshpass -p <PW> scp $O -q /tmp/nav2_params.yaml $J:/home/jetson/ros2_ws/src/rover_navigation/config/nav2_params.yaml || exit 1
sshpass -p <PW> ssh $O $J "cd ~/ros2_ws && source /opt/ros/humble/setup.bash && colcon build --packages-select rover_navigation rover_bringup 2>&1 | tail -1; grep -c 'transform_tolerance: 0.5' install/rover_navigation/share/rover_navigation/config/nav2_params.yaml; sha256sum install/rover_bringup/lib/rover_bringup/rf2o_gate.py | cut -c1-12"
