#!/bin/bash
# 09-29 §13.5 nav_guard 재개입 방지 수정 빌드(다음 prep 부터 적용)
cd ~/ros2_ws && colcon build --packages-select rover_bringup 2>&1 | tail -1; grep -c tripped install/rover_bringup/lib/rover_bringup/nav_guard.py
