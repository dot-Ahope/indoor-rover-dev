#!/bin/bash
# 09-29 §13 L2: nav_guard 배포·빌드·기동 확인(목표 없이 8 s — 개입 0 이어야)
set +u; cd ~/ros2_ws; colcon build --packages-select rover_bringup rover_navigation 2>&1 | tail -1
source install/setup.bash
ls -la install/rover_bringup/lib/rover_bringup/nav_guard.py | cut -c1-60
ros2 launch rover_navigation navigation.launch.py --show-args 2>/dev/null | grep -aA1 "'nav_guard'"
timeout -s INT 8 ros2 run rover_bringup nav_guard.py --ros-args -r __node:=nav_guard_smoke 2>&1 | grep -av "^$" | tail -6
echo "rc(124=정상 종료 by timeout): $?"
