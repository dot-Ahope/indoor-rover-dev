#!/bin/bash
# (10-15 §30) 배포 확인 — 로버 안 움직임
for f in ~/ros2_ws/src/rover_navigation/config/nav2_params.yaml ~/ros2_ws/install/rover_navigation/share/rover_navigation/config/nav2_params.yaml /tmp/nav2_params.yaml; do echo "$f: $(grep -n 'ClearanceBandCritic: {' $f | cut -c1-60)"; done
ls -la ~/ros2_ws/install/rover_navigation/share/rover_navigation/config/nav2_params.yaml
