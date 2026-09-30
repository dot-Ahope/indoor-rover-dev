#!/bin/bash
# 09-30 §4: slam·joy launch 인자 배포 확인
cd ~/ros2_ws && colcon build --packages-select rover_bringup 2>&1 | tail -1; source install/setup.bash
ros2 launch rover_bringup slam.launch.py --show-args 2>/dev/null | grep -aA1 "map_file\|map_start_pose"
ros2 launch rover_bringup joy_teleop.launch.py --show-args 2>/dev/null | grep -aA1 "profile"
mkdir -p ~/maps/office; ls -ld ~/maps/office
