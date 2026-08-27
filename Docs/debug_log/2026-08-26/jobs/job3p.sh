#!/bin/bash
# 슬립 보정 검증: 회전 3초 → filtered Δyaw ≈ 실회전(~15°) 확인 (wheel은 ~35° 주장 예상)
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
echo "===ROTATE 0.3rad/s 3s==="
ros2 topic pub -r 10 -t 30 -w 1 /cmd_vel geometry_msgs/msg/Twist '{angular: {z: 0.3}}' >/dev/null 2>&1 &
P=$!; wait $P
ros2 topic pub -t 5 -r 10 -w 1 /cmd_vel geometry_msgs/msg/Twist '{}' >/dev/null 2>&1
echo "===AFTER==="
snap
