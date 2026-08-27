#!/bin/bash
# 자이로 생사 판정 녹화: 90초간 gyro z 50Hz 연속 기록 (사용자가 손으로 로버 회전)
source /opt/ros/humble/setup.bash
rm -f /tmp/gyro_rec.txt
setsid nohup bash -c 'source /opt/ros/humble/setup.bash; timeout 90 ros2 topic echo /imu/data_raw --field angular_velocity.z > /tmp/gyro_rec.txt 2>/dev/null' >/dev/null 2>&1 &
echo "RECORDING_STARTED (90s)"
