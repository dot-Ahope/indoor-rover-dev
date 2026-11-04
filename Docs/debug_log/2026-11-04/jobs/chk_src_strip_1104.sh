#!/bin/bash
# 11-04: 주석 뺀 md5 비교(읽기만)
python3 /tmp/anal_src_strip_md5.py /home/jetson/ros2_ws/src rover_navigation/config/nav2_params.yaml rover_navigation/config/nvblox_local.yaml rover_navigation/config/nav_to_pose_no_spin.xml rover_navigation/launch/navigation.launch.py rover_bringup/scripts/pad_relief.py rover_bringup/scripts/rf2o_gate.py
