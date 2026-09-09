#!/bin/bash
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "=== 보드 상태 (스톨·래치) ==="
timeout 8 ros2 topic echo /rover/status --once 2>/dev/null | grep -aE "level|message:|value:" | head -6
echo "=== 배터리 5회 ==="
for i in 1 2 3 4 5; do timeout 4 ros2 topic echo /battery --once 2>/dev/null | grep -aoE "voltage: [0-9.]+"; done
echo "=== TF/EKF 생존 ==="
for t in /tf /odometry/filtered /wheel_odom /map; do printf "  %-20s " "$t"; timeout 8 ros2 topic hz "$t" 2>&1 | grep -aoE "average rate: [0-9.]+" | tail -1 || echo 무발행; done
echo "  /odometry/filtered 퍼블리셔: $(timeout 6 ros2 topic info /odometry/filtered 2>/dev/null | grep -aoE 'Publisher count: [0-9]+')"
echo "  fastrtps 잔재: $(ls /dev/shm 2>/dev/null | grep -c fastrtps)"
echo "=== nav2 로그 ==="
grep -aiE "cancel|abort|stuck|collision|backup|recovery|fail" /tmp/nav2.log | tail -6 | cut -c1-140
echo "=== load ==="
cut -d' ' -f1-3 /proc/loadavg
