#!/bin/bash
# EKF 진단: 구독 QoS 정합, 정지 시 자이로 바이어스, 30초 yaw 드리프트
source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash

echo "===QOS_WHEEL_ODOM==="
ros2 topic info /wheel_odom --verbose 2>/dev/null | grep -E "Node name:|Endpoint type:|Reliability:"
echo "===QOS_IMU==="
ros2 topic info /imu/data_raw --verbose 2>/dev/null | grep -E "Node name:|Endpoint type:|Reliability:"
echo "===GYRO_AT_REST==="
timeout 6 ros2 topic echo /imu/data_raw --once --field angular_velocity 2>/dev/null
echo "===FILTERED_YAW_T0==="
date +%s.%N
timeout 6 ros2 topic echo /odometry/filtered --once --field pose.pose.orientation 2>/dev/null
sleep 30
echo "===FILTERED_YAW_T30==="
date +%s.%N
timeout 6 ros2 topic echo /odometry/filtered --once --field pose.pose.orientation 2>/dev/null
echo "===FILTERED_TWIST==="
timeout 6 ros2 topic echo /odometry/filtered --once --field twist.twist 2>/dev/null
