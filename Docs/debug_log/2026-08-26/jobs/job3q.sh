#!/bin/bash
# 고속 회전 슬립 테스트: 0.6 rad/s × 3s — 계수 0.43의 속도 의존성 확인
source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash

snap() {
  echo "--- wheel_odom yaw quat ---"
  timeout 6 ros2 topic echo /wheel_odom --once --field pose.pose.orientation 2>/dev/null | grep -E "^[zw]"
  echo "--- filtered yaw quat ---"
  timeout 6 ros2 topic echo /odometry/filtered --once --field pose.pose.orientation 2>/dev/null | grep -E "^[zw]"
}

echo "===BEFORE==="
snap
echo "===ROTATE 0.6rad/s 3s==="
ros2 topic pub -r 10 -t 30 -w 1 /cmd_vel geometry_msgs/msg/Twist '{angular: {z: 0.6}}' >/dev/null 2>&1 &
P=$!; sleep 1.5
echo "--- mid wheel vyaw (원본) ---"
timeout 4 ros2 topic echo /wheel_odom --once --field twist.twist.angular.z 2>/dev/null
echo "--- mid filtered vyaw (보정 후) ---"
timeout 4 ros2 topic echo /odometry/filtered --once --field twist.twist.angular.z 2>/dev/null
wait $P
ros2 topic pub -t 5 -r 10 -w 1 /cmd_vel geometry_msgs/msg/Twist '{}' >/dev/null 2>&1
echo "===AFTER==="
snap
