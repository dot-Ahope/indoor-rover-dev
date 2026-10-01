#!/bin/bash
# 10-01 §8.5: slam.launch.py(transform_timeout 0.5) 배포·빌드
cp /tmp/f14/slam.launch.py ~/ros2_ws/src/rover_bringup/launch/ && cd ~/ros2_ws && colcon build --packages-select rover_bringup 2>&1 | tail -1
grep -n "'transform_timeout': 0.5" ~/ros2_ws/install/rover_bringup/share/rover_bringup/launch/slam.launch.py
