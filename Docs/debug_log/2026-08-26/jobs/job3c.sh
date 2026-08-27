#!/bin/bash
# 누락 의존성 설치 후 EKF 재기동·검증
echo '<PW>' | sudo -S apt-get install -y ros-humble-diagnostic-updater 2>&1 | tail -2
source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash

pkill -f "ekf_node" 2>/dev/null || true
sleep 1
setsid nohup ros2 launch rover_bringup ekf.launch.py > /tmp/ekf.log 2>&1 &
sleep 12

echo "===EKF_LOG_TAIL==="
tail -4 /tmp/ekf.log
echo "===HZ_FILTERED==="
timeout 10 ros2 topic hz /odometry/filtered 2>&1 | tail -2 || true
echo "===FILTERED_POSE==="
timeout 6 ros2 topic echo /odometry/filtered --once --field pose.pose 2>/dev/null | head -12 || echo NO_FILTERED_MSG
echo "===EKF_SUB_QOS==="
ros2 topic info /wheel_odom --verbose 2>/dev/null | grep -A2 -E "Node name: ekf" | head -6
ros2 topic info /wheel_odom --verbose 2>/dev/null | grep -B4 "SUBSCRIPTION" | grep -E "Node name|Reliability" | head -4
