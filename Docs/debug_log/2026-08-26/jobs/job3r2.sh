#!/bin/bash
# 자이로 판정 재녹화: 180초간 gyro z 50Hz 연속 기록 (사용자 손 회전 대기)
source /opt/ros/humble/setup.bash
pkill -f "gyro_rec" 2>/dev/null || true
rm -f /tmp/gyro_rec.txt
setsid nohup bash -c 'source /opt/ros/humble/setup.bash; timeout 180 ros2 topic echo /imu/data_raw --field angular_velocity.z > /tmp/gyro_rec.txt 2>/dev/null' >/dev/null 2>&1 &
sleep 2
# 녹화가 실제로 흐르는지 즉시 확인
sleep 3
LINES=$(grep -c . /tmp/gyro_rec.txt 2>/dev/null || echo 0)
echo "RECORDING_STARTED (180s) — first 5s lines: $LINES"
