#!/bin/bash
echo "실행 중 stuck_monitor use_gyro: $(timeout 15 ros2 param get /stuck_monitor use_gyro 2>&1 | tail -1)"
grep -n "use_gyro" ~/ros2_ws/install/rover_navigation/share/rover_navigation/launch/navigation.launch.py | head -3
