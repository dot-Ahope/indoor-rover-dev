#!/bin/bash
# 손 회전 동적 검증 녹화 150s: 광학 y(=로봇 yaw축) 자이로 + EKF yaw 각속도
source /opt/ros/humble/setup.bash
pkill -f "gyro_rec|yaw_rec" 2>/dev/null; rm -f /tmp/gyro_rec.txt /tmp/yaw_rec.txt
setsid nohup bash -c 'source /opt/ros/humble/setup.bash; timeout 180 ros2 topic echo /imu/data --field angular_velocity.y > /tmp/gyro_rec.txt 2>/dev/null' >/dev/null 2>&1 &
setsid nohup bash -c 'source /opt/ros/humble/setup.bash; timeout 180 ros2 topic echo /odometry/filtered --field twist.twist.angular.z > /tmp/yaw_rec.txt 2>/dev/null' >/dev/null 2>&1 &
sleep 4; echo "RECORDING (180s) gyro_lines=$(grep -c . /tmp/gyro_rec.txt) ekf_lines=$(grep -c . /tmp/yaw_rec.txt)"
