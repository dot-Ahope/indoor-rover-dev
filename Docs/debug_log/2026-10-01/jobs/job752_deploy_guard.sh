#!/bin/bash
# 10-01 §8.13: nav_guard d0 수정 배포·빌드
cp /tmp/f14/nav_guard.py ~/ros2_ws/src/rover_bringup/scripts/ && cd ~/ros2_ws && colcon build --packages-select rover_bringup 2>&1 | tail -1
grep -c "d0_window" ~/ros2_ws/install/rover_bringup/lib/rover_bringup/nav_guard.py
