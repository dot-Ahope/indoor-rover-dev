#!/bin/bash
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "=== 현재 사방 여유 ==="; bash /tmp/job21c_where.sh | sed -n '3,20p'
echo "=== nav2.log MPPI/컨트롤러 경고 (최근) ==="
grep -aiE "mppi|collision|critic|trajector|Failed|abort|recovery|spin|backup" /tmp/nav2.log | grep -av "get_state\|get_param" | tail -12 || echo "  없음"
echo "=== 배터리 ==="; timeout 5 ros2 topic echo /battery --once 2>/dev/null | grep -aoE "voltage: [0-9.]+"
echo "=== 정지 확인 ==="; timeout 3 ros2 topic echo /cmd_vel --once 2>/dev/null | grep -aE "^  x:|^  z:" | head -2 || echo "  cmd_vel 무발행(정지)"
