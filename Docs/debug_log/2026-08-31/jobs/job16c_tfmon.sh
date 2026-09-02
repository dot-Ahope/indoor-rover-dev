#!/bin/bash
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "=== odom -> base_link (EKF) ==="
timeout 8 ros2 run tf2_ros tf2_monitor odom base_link 2>/dev/null | tail -20
echo ""
echo "=== map -> odom (slam) ==="
timeout 8 ros2 run tf2_ros tf2_monitor map odom 2>/dev/null | tail -20
