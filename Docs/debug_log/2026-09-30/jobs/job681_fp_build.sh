#!/bin/bash
# 09-30 §3: footprint 실측 반영 빌드
cd ~/ros2_ws && colcon build --packages-select rover_navigation 2>&1 | tail -1; grep -c "0.262" install/rover_navigation/share/rover_navigation/config/nav2_params.yaml
