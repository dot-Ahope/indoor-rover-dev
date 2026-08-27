#!/bin/bash
# 접지 상태 초저속 주행 테스트 (사용자 승인, 2026-08-26)
# 한계: linear.x<=0.08, angular.z<=0.8 (지시서 §3) — 사용값 0.05 / 0.3
source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash

odom_pose() { timeout 6 ros2 topic echo /wheel_odom --once --field pose.pose 2>/dev/null; }
stop_cmd()  { ros2 topic pub -t 5 -r 10 -w 1 /cmd_vel geometry_msgs/msg/Twist '{}' >/dev/null 2>&1; }

echo "===ODOM_BEFORE==="
odom_pose

echo "===PHASE1_ROTATE (angular.z=0.3, 3s)==="
ros2 topic pub -r 10 -t 30 -w 1 /cmd_vel geometry_msgs/msg/Twist '{angular: {z: 0.3}}' >/dev/null 2>&1 &
PUB=$!
sleep 1.5
echo "--- mid-motion twist ---"
timeout 4 ros2 topic echo /wheel_odom --once --field twist.twist 2>/dev/null
wait $PUB
stop_cmd
echo "===ODOM_AFTER_ROTATE==="
odom_pose

echo "===PHASE2_FORWARD (linear.x=0.05, 3s)==="
ros2 topic pub -r 10 -t 30 -w 1 /cmd_vel geometry_msgs/msg/Twist '{linear: {x: 0.05}}' >/dev/null 2>&1 &
PUB=$!
sleep 1.5
echo "--- mid-motion twist ---"
timeout 4 ros2 topic echo /wheel_odom --once --field twist.twist 2>/dev/null
wait $PUB
stop_cmd
echo "===ODOM_AFTER_FORWARD==="
odom_pose

echo "===PHASE3_BACKWARD (linear.x=-0.05, 3s)==="
ros2 topic pub -r 10 -t 30 -w 1 /cmd_vel geometry_msgs/msg/Twist '{linear: {x: -0.05}}' >/dev/null 2>&1 &
PUB=$!
wait $PUB
stop_cmd
echo "===ODOM_AFTER_BACKWARD==="
odom_pose

echo "===FINAL_STOP_TWIST==="
timeout 4 ros2 topic echo /wheel_odom --once --field twist.twist 2>/dev/null
