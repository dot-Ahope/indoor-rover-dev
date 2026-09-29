#!/bin/bash
# 09-29 §3: ekf.launch.py(icr·rot_cov 인자) 배포 후 rover_bringup 빌드·확인
set +u; cd ~/ros2_ws
colcon build --packages-select rover_bringup 2>&1 | tail -1
source install/setup.bash
echo "설치된 인자:"; ros2 launch rover_bringup ekf.launch.py --show-args 2>/dev/null | grep -aA1 "'icr'\|'rot_cov'"
