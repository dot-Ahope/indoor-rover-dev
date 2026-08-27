#!/bin/bash
# Step 3 주행 검증: 회전·직진 시 /odometry/filtered 발산 없음 확인
# (지시서 §3 한계 내: angular 0.3 rad/s, linear 0.05 m/s)
source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash

snap() {
  echo "--- wheel_odom pose ---"
  timeout 6 ros2 topic echo /wheel_odom --once --field pose.pose 2>/dev/null | grep -E "^\s+[xyzw]:" | head -7
  echo "--- filtered pose ---"
  timeout 6 ros2 topic echo /odometry/filtered --once --field pose.pose 2>/dev/null | grep -E "^\s+[xyzw]:" | head -7
}

echo "===BEFORE==="
snap

echo "===ROTATE 0.3rad/s 3s==="
ros2 topic pub -r 10 -t 30 -w 1 /cmd_vel geometry_msgs/msg/Twist '{angular: {z: 0.3}}' >/dev/null 2>&1 &
P=$!; sleep 1.5
echo "--- mid filtered vyaw vs gyro ---"
timeout 4 ros2 topic echo /odometry/filtered --once --field twist.twist.angular.z 2>/dev/null
timeout 4 ros2 topic echo /imu/data --once --field angular_velocity.z 2>/dev/null
wait $P
ros2 topic pub -t 5 -r 10 -w 1 /cmd_vel geometry_msgs/msg/Twist '{}' >/dev/null 2>&1
echo "===AFTER_ROTATE==="
snap

echo "===FORWARD 0.05m/s 3s==="
ros2 topic pub -r 10 -t 30 -w 1 /cmd_vel geometry_msgs/msg/Twist '{linear: {x: 0.05}}' >/dev/null 2>&1 &
P=$!; sleep 1.5
echo "--- mid filtered vx ---"
timeout 4 ros2 topic echo /odometry/filtered --once --field twist.twist.linear.x 2>/dev/null
wait $P
ros2 topic pub -t 5 -r 10 -w 1 /cmd_vel geometry_msgs/msg/Twist '{}' >/dev/null 2>&1
echo "===AFTER_FORWARD==="
snap

echo "===BACKWARD 0.05m/s 3s==="
ros2 topic pub -r 10 -t 30 -w 1 /cmd_vel geometry_msgs/msg/Twist '{linear: {x: -0.05}}' >/dev/null 2>&1 &
P=$!; wait $P
ros2 topic pub -t 5 -r 10 -w 1 /cmd_vel geometry_msgs/msg/Twist '{}' >/dev/null 2>&1
echo "===AFTER_BACKWARD==="
snap

echo "===FINAL_FILTERED_TWIST==="
timeout 4 ros2 topic echo /odometry/filtered --once --field twist.twist 2>/dev/null
