#!/bin/bash
# 11-04: Jetson src 파일 md5(CR 제거) — 저장소와 비교용, 읽기만
for f in rover_navigation/config/nav2_params.yaml rover_navigation/config/nvblox_local.yaml rover_navigation/config/nav_to_pose_no_spin.xml rover_navigation/launch/navigation.launch.py rover_bringup/launch/ekf.launch.py rover_bringup/launch/camera.launch.py rover_bringup/scripts/pad_relief.py rover_bringup/scripts/rf2o_gate.py; do echo "$(tr -d '\r' < ~/ros2_ws/src/$f | md5sum | cut -c1-8) $f"; done
