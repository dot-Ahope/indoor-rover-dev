#!/bin/bash
# (10-14 §14) Jetson 소스의 rover_navigation 파일 3 개를 /tmp 로 복사(PC 에서 저장소와 비교하려고) — 로버 안 움직임
R=~/ros2_ws/src/rover_navigation; cp $R/CMakeLists.txt /tmp/j_CMakeLists.txt; cp $R/config/nav2_params.yaml /tmp/j_nav2_params.yaml; cp $R/config/nav_to_pose_no_spin.xml /tmp/j_bt.xml; ls -la /tmp/j_* | awk "{print \$5, \$9}"; ls $R/src/
