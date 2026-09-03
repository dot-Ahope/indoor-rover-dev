#!/bin/bash
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
pkill -f sensor_conditioner; pkill -f ekf_node; sleep 2
setsid nohup ros2 launch rover_bringup ekf.launch.py > /tmp/ekf.log 2>&1 &
sleep 15
grep -a "gyro bias\|not stationary" /tmp/ekf.log | tail -1
echo -n "/odometry/filtered: "; timeout 5 ros2 topic hz /odometry/filtered 2>&1 | grep -aoE "average rate: [0-9.]+" | head -1
