#!/bin/bash
# 10-01 §8.17: BT(경로 무효 시만 재계획) 배포·빌드
cp /tmp/f14/nav_to_pose_no_spin.xml ~/ros2_ws/src/rover_navigation/config/ && cd ~/ros2_ws && colcon build --packages-select rover_navigation 2>&1 | tail -1
grep -c "IsPathValid" ~/ros2_ws/install/rover_navigation/share/rover_navigation/config/nav_to_pose_no_spin.xml
