#!/bin/bash
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "=== nav2 로그: 중단·복구·취소 ==="
grep -aiE "collision|abort|cancel|backup|recovery|stuck|fail|progress" /tmp/nav2.log | tail -18 | cut -c1-160
echo ""
echo "=== 건전성 ==="
echo "  EKF 주기 위반: $(grep -ac 'Failed to meet update rate' /tmp/sensors.log 2>/dev/null)회"
echo "  slam 스캔 폐기: $(grep -ac 'Message Filter dropping' /tmp/slam.log 2>/dev/null)회"
echo "  load: $(cut -d' ' -f1-3 /proc/loadavg)"
echo "  /tf 퍼블리셔: $(timeout 6 ros2 topic info /tf 2>/dev/null | grep -aoE 'Publisher count: [0-9]+')"
echo "  배터리: $(timeout 5 ros2 topic echo /battery --once 2>/dev/null | grep -aoE 'voltage: [0-9.]+')"
echo "  보드: $(timeout 6 ros2 topic echo /rover/status --once 2>/dev/null | grep -aE 'message:' | head -1)"
