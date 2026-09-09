#!/bin/bash
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "=== nav2 로그 마지막 (취소/복구 사유) ==="
grep -aiE "cancel|abort|recovery|backup|stuck|fail|collision|invalid|timeout|goal" /tmp/nav2.log | tail -20 | cut -c1-160
echo ""
echo "=== stuck_monitor 관련 로그 ==="
grep -aiE "stuck" /tmp/nav2.log | tail -12 | cut -c1-160
echo ""
echo "=== /rover/stuck 최근 값 ==="
timeout 6 ros2 topic echo /rover/stuck --once 2>/dev/null | head -6 || echo "  (무발행)"
echo ""
echo "=== stuck_monitor 파라미터 ==="
timeout 8 ros2 param dump /stuck_monitor 2>/dev/null | head -20 || echo "  (노드 없음)"
