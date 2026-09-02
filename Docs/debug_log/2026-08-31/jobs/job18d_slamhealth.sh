#!/bin/bash
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "=== slam 로그 (드롭/경고) ==="
grep -aiE "drop|reject|fail|warn|queue|match" /tmp/slam.log 2>/dev/null | tail -8 || echo "  (없음)"
echo "=== 현재 map->odom (slam이 보정한 양) ==="
timeout 5 ros2 run tf2_ros tf2_echo map odom 2>/dev/null | grep -aE "Translation|RPY \(degree\)" | head -2
echo "=== 현재 odom / map->base ==="
timeout 4 ros2 topic echo /odometry/filtered --once 2>/dev/null | grep -aA2 "position:" | grep -aoE "[xy]: [-0-9.e]+" | head -2 | tr '\n' ' '; echo
timeout 5 ros2 run tf2_ros tf2_echo map base_link 2>/dev/null | grep -aE "Translation" | head -1
echo "=== 휠 오도 원시 vs EKF (슬립 판단용) ==="
echo -n "  /wheel_odom x: "; timeout 4 ros2 topic echo /wheel_odom --once 2>/dev/null | grep -aA2 "position:" | grep -aoE "x: [-0-9.e]+" | head -1
echo "=== /map 발행 (slam이 맵을 만들고 있나) ==="
timeout 6 ros2 topic hz /map 2>&1 | grep -aoE "average rate: [0-9.]+" | head -1 || echo "  /map 무발행"
