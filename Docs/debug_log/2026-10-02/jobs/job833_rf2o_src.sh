#!/bin/bash
# 10-02 §13 R0: rf2o 소스 확인 — 인터넷·브랜치·메시지(공분산 채우는지)
timeout 10 git ls-remote https://github.com/MAPIRlab/rf2o_laser_odometry.git 2>&1 | grep -E "heads/(ros2|humble|master)" | head
timeout 10 git ls-remote https://github.com/Adlink-ROS/rf2o_laser_odometry.git 2>&1 | grep -E "heads/" | head
dpkg -l | grep -i rf2o | head -2
ls ~/ros2_ws/src
