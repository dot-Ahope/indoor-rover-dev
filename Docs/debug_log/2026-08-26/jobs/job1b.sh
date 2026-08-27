#!/bin/bash
# Step 1 검증: 토픽 목록, 발행 주기, 배터리 전압
source /opt/ros/humble/setup.bash
echo "===TOPIC_LIST==="
ros2 topic list
echo "===HZ_WHEEL_ODOM==="
timeout 12 ros2 topic hz /wheel_odom --qos-reliability best_effort 2>&1 | tail -4 || true
echo "===HZ_IMU==="
timeout 12 ros2 topic hz /imu/data_raw --qos-reliability best_effort 2>&1 | tail -4 || true
echo "===BATTERY==="
timeout 10 ros2 topic echo /battery --once 2>&1 | head -20 || true
