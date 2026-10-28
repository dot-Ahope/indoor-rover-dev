#!/bin/bash
# 10-28 하루 시작 점검(읽기만): 가동 시간 · Wi-Fi · /tmp prep 스크립트 · 스택 프로세스 · SLAM transform_timeout · 수정 nvblox 층 · 디스크
uptime; echo "Wi-Fi $(iwgetid -r)"
ls /tmp/prep_fast.sh /tmp/prep_patrol.sh /tmp/chk_prep.py /tmp/prep_smac_1027.sh /tmp/chk_drive_gate.py 2>&1 | tr "\n" " "; echo
echo "nav2 $(pgrep -fc controller_server) · slam $(pgrep -fc localization_slam_toolbox_node) · cam $(pgrep -fc realsense2_camera) · agent $(docker ps --format '{{.Names}}' | grep -c microros_agent) · nvblox $(docker exec isaac_ros_dev-aarch64-container bash -c "pgrep -fc '^/opt/ros/humble/lib/nvblox_ros/nvblox_node' || true" 2>/dev/null)"
echo "slam.launch transform_timeout: $(grep -o "'transform_timeout': [0-9.]*" ~/ros2_ws/src/rover_bringup/launch/slam.launch.py) · nvblox 층 return 수정: $(grep -c '2026-10-27 수정' ~/workspaces/isaac_ros-dev/src/isaac_ros_nvblox/nvblox_nav2/src/nvblox_costmap_layer.cpp)"
echo "배터리: $(grep -a 'V$\| V ' /tmp/prepchk.txt 2>/dev/null | tail -1 | cut -c1-90)"; df -h / | tail -1
