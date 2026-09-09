#!/bin/bash
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "=== 현재 TF 체인 ==="
for pair in "map odom" "odom base_link" "map base_link"; do
  printf "  %-18s " "$pair"
  timeout 10 ros2 run tf2_ros tf2_echo $pair 2>&1 | grep -aE "Translation|Rotation: in RPY \(degree\)" | tail -2 | tr '\n' ' '; echo
done
echo ""
echo "=== EKF 출력 (map 기준 아님, odom 기준) ==="
timeout 6 ros2 topic echo /odometry/filtered --once 2>/dev/null | grep -aE "^      x:|^      y:" | head -2
echo ""
echo "=== SLAM 맵 범위 vs 로버 위치 ==="
timeout 10 ros2 topic echo /map --once --field info 2>/dev/null | head -12
echo ""
echo "=== slam_toolbox 경고/오류 ==="
grep -aiE "warn|error|loop|reject|fail|jump" /tmp/slam.log 2>/dev/null | tail -12 | cut -c1-150
echo ""
echo "=== nav2 로그: 취소 이후 ==="
awk '/Goal canceled/{f=1} f' /tmp/nav2.log 2>/dev/null | tail -15 | cut -c1-150
echo ""
echo "=== sensor_conditioner 슬립/스케일 경고 ==="
grep -aiE "slip|scale|reject|warn" /tmp/sensors.log 2>/dev/null | grep -ai conditioner | tail -6 | cut -c1-150
