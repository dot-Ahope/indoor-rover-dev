#!/bin/bash
# 휠 단독 EKF 반영 → 재기동 → 정적 검증 (yaw 완전 고정 기대)
set -e
source /opt/ros/humble/setup.bash
cp -r /tmp/rover_src/rover_bringup ~/ros2_ws/src/
chmod +x ~/ros2_ws/src/rover_bringup/scripts/sensor_conditioner.py
cd ~/ros2_ws
colcon build --symlink-install --packages-select rover_bringup 2>&1 | tail -2

source ~/ros2_ws/install/setup.bash
pkill -f "ekf.launch" 2>/dev/null || true
pkill -f "ekf_node" 2>/dev/null || true
pkill -f "sensor_conditioner" 2>/dev/null || true
sleep 1
setsid nohup ros2 launch rover_bringup ekf.launch.py > /tmp/ekf.log 2>&1 &
sleep 15

echo "===EKF_ERRORS==="
grep -aE "error|died|FATAL" /tmp/ekf.log | tail -3 || echo NONE
echo "===HZ_FILTERED==="
timeout 8 ros2 topic hz /odometry/filtered 2>&1 | tail -2 || true
echo "===YAW_T0==="
timeout 6 ros2 topic echo /odometry/filtered --once --field pose.pose.orientation 2>/dev/null | grep -E "^[zw]"
sleep 45
echo "===YAW_T45==="
timeout 6 ros2 topic echo /odometry/filtered --once --field pose.pose.orientation 2>/dev/null | grep -E "^[zw]"
echo "===POS_T45==="
timeout 6 ros2 topic echo /odometry/filtered --once --field pose.pose.position 2>/dev/null
