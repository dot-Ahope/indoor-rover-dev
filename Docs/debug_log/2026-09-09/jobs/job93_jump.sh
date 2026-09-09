#!/bin/bash
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "=== 현재 TF ==="
echo -n "map->odom : "; timeout 5 ros2 run tf2_ros tf2_echo map odom 2>/dev/null | grep -aE "Translation|Rotation: in RPY \(degree\)" | head -2 | tr '\n' ' '; echo
echo -n "odom->base: "; timeout 5 ros2 run tf2_ros tf2_echo odom base_link 2>/dev/null | grep -aE "Translation|Rotation: in RPY \(degree\)" | head -2 | tr '\n' ' '; echo
echo -n "map->base : "; timeout 5 ros2 run tf2_ros tf2_echo map base_link 2>/dev/null | grep -aE "Translation|Rotation: in RPY \(degree\)" | head -2 | tr '\n' ' '; echo
echo ""
echo "=== EKF odom (휠+자이로 적분) ==="
timeout 5 ros2 topic echo /odometry/filtered --once 2>/dev/null | grep -aE "^      x:|^      y:" | head -2
echo ""
echo "=== 보드 원시 odom ==="
timeout 5 ros2 topic echo /wheel_odom --once 2>/dev/null | grep -aE "^      x:|^      y:" | head -2
echo ""
echo "=== slam_toolbox 로그 (최근) ==="
grep -aiE "warn|error|loop|match|jump|reset|serial" /tmp/slam.log | tail -15
echo ""
echo "=== nav2 로그 (최근 abort 사유) ==="
grep -aiE "abort|fail|invalid|goal|recovery|collision|stuck" /tmp/nav2.log | tail -12
echo ""
echo "=== stuck_monitor ==="
timeout 4 ros2 topic echo /rover/stuck --once 2>/dev/null | head -4 || echo "  (무발행)"
echo ""
echo "=== 맵 크기 ==="
timeout 6 ros2 topic echo /map --once --field info 2>/dev/null | head -8
