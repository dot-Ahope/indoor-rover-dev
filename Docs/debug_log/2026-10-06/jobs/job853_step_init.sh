#!/bin/bash
# 10-06 §4: 단계별 회전 실측 — bag 기록 시작(/imu/data 포함) + init
source ~/rf2o_ws/install/setup.bash 2>/dev/null
pkill -INT -f "ros2 bag record -o /tmp/bag_step" 2>/dev/null; sleep 1; rm -rf /tmp/bag_step1
setsid nohup ros2 bag record -o /tmp/bag_step1 /scan /tf /tf_static /imu/data /wheel_odom /cmd_vel /odom_rf2o /odom_rf2o/gated /odometry/filtered /odometry/ekf_a /local_costmap/costmap /map > /tmp/bag_step1.log 2>&1 < /dev/null &
sleep 4; python3 -u /tmp/step_rot.py init 2>&1 | grep -av "^\["
