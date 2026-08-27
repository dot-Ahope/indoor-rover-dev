#!/bin/bash
# IMU 실물 여부 판정: 정지 시 중력벡터(≈9.8) + 샘플 간 변동(실센서 노이즈) 확인
source /opt/ros/humble/setup.bash
echo "===ACCEL_SAMPLE_1==="
timeout 6 ros2 topic echo /imu/data_raw --once --field linear_acceleration 2>/dev/null
echo "===ACCEL_SAMPLE_2==="
timeout 6 ros2 topic echo /imu/data_raw --once --field linear_acceleration 2>/dev/null
echo "===GYRO_SAMPLE_1==="
timeout 6 ros2 topic echo /imu/data_raw --once --field angular_velocity 2>/dev/null
echo "===GYRO_SAMPLE_2==="
timeout 6 ros2 topic echo /imu/data_raw --once --field angular_velocity 2>/dev/null
echo "===MAG_SAMPLE==="
timeout 6 ros2 topic echo /imu/mag --once --field magnetic_field 2>/dev/null
