#!/bin/bash
# (10-15 §26) 배포 전 Jetson src 파일 md5 — 읽기만
cd ~/ros2_ws/src/rover_navigation; for f in CMakeLists.txt package.xml config/nav2_params.yaml config/nav_to_pose_no_spin.xml config/nvblox_local.yaml; do echo "$f JETSON $(tr -d '\r' < $f | md5sum | cut -c1-10)"; done
