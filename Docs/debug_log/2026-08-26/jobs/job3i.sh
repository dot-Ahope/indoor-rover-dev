#!/bin/bash
# 컨디셔너 10s 캘리브레이션 반영 → EKF 재기동 → 60초 정적 드리프트 정량 측정
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
sleep 20

echo "===CALIB_LOG==="
grep -a "bias" /tmp/ekf.log | tail -1
echo "===YAW_T0==="
timeout 6 ros2 topic echo /odometry/filtered --once --field pose.pose.orientation 2>/dev/null | grep -E "^[zw]"
sleep 60
echo "===YAW_T60==="
timeout 6 ros2 topic echo /odometry/filtered --once --field pose.pose.orientation 2>/dev/null | grep -E "^[zw]"
echo "===POS_T60==="
timeout 6 ros2 topic echo /odometry/filtered --once --field pose.pose.position 2>/dev/null
