#!/bin/bash
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "=== /rover/status (스톨·래치) ==="
timeout 8 ros2 topic echo /rover/status --once 2>/dev/null | grep -aE "level|name:|message:|key:|value:" | head -14
echo ""
echo "=== 배터리 3회 ==="
for i in 1 2 3; do timeout 5 ros2 topic echo /battery --once 2>/dev/null | grep -aoE "voltage: [0-9.]+"; done
echo ""
echo "=== 휠 오도메트리 (정지 상태 확인) ==="
timeout 6 ros2 topic echo /wheel_odom --once 2>/dev/null | grep -aE "^      x:|^      y:" | head -2
echo ""
echo "=== nav2 로그 마지막 ==="
grep -aiE "cancel|abort|stuck|collision|backup|recovery|fail" /tmp/nav2.log | tail -10 | cut -c1-150
