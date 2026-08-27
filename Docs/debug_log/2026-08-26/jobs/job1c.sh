#!/bin/bash
# Step 1 검증(계속): Humble hz는 QoS 플래그 없음 → 플레인 hz 시도, 실패 시 echo 카운트로 측정
source /opt/ros/humble/setup.bash
echo "===HZ_WHEEL_ODOM_PLAIN==="
timeout 12 ros2 topic hz /wheel_odom 2>&1 | tail -3 || true
echo "===HZ_IMU_PLAIN==="
timeout 12 ros2 topic hz /imu/data_raw 2>&1 | tail -3 || true
echo "===COUNT_WHEEL_ODOM_10S==="
N=$(timeout 10 ros2 topic echo /wheel_odom --qos-reliability best_effort --field header.stamp.sec 2>/dev/null | grep -c '^[0-9]')
echo "wheel_odom msgs in 10s: $N (=> $((N/10)) Hz)"
echo "===COUNT_IMU_10S==="
N=$(timeout 10 ros2 topic echo /imu/data_raw --qos-reliability best_effort --field header.stamp.sec 2>/dev/null | grep -c '^[0-9]')
echo "imu msgs in 10s: $N (=> $((N/10)) Hz)"
