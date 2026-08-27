#!/bin/bash
# 센서 컨디셔너 반영 → 재빌드 → EKF 재기동 → 정적 재검증 (바이어스 제거 확인)
set -e
source /opt/ros/humble/setup.bash

cp -r /tmp/rover_src/rover_bringup ~/ros2_ws/src/
chmod +x ~/ros2_ws/src/rover_bringup/scripts/sensor_conditioner.py
cd ~/ros2_ws
echo "===COLCON_BUILD==="
colcon build --symlink-install --packages-select rover_bringup 2>&1 | tail -3

source ~/ros2_ws/install/setup.bash
pkill -f "ekf_node" 2>/dev/null || true
pkill -f "sensor_conditioner" 2>/dev/null || true
pkill -f "ekf.launch" 2>/dev/null || true
sleep 1
setsid nohup ros2 launch rover_bringup ekf.launch.py > /tmp/ekf.log 2>&1 &
sleep 15

echo "===EKF_LOG==="
grep -aE "bias|error|died|WARN" /tmp/ekf.log | tail -4
echo "===HZ_FILTERED==="
timeout 8 ros2 topic hz /odometry/filtered 2>&1 | tail -2 || true
echo "===GYRO_CONDITIONED==="
timeout 6 ros2 topic echo /imu/data --once --field angular_velocity 2>/dev/null
echo "===YAW_T0==="
timeout 6 ros2 topic echo /odometry/filtered --once --field pose.pose.orientation 2>/dev/null | grep -E "^[zw]"
sleep 30
echo "===YAW_T30==="
timeout 6 ros2 topic echo /odometry/filtered --once --field pose.pose.orientation 2>/dev/null | grep -E "^[zw]"
echo "===FILTERED_VYAW==="
timeout 6 ros2 topic echo /odometry/filtered --once --field twist.twist.angular 2>/dev/null
