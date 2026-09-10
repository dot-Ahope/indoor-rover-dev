#!/bin/bash
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "=== 복구 행동 상태 토픽 존재/타입 ==="
for a in backup spin drive_on_heading wait assisted_teleop; do
  t="/$a/_action/status"
  printf "  %-34s " "$t"
  ros2 topic info "$t" 2>/dev/null | grep -aoE "Type: .*" | head -1 || echo "없음"
done
echo ""
echo "=== stuck_monitor 가 실제로 구독 중인가 ==="
timeout 8 ros2 node info /stuck_monitor 2>/dev/null | sed -n '/Subscribers/,/Publishers/p' | sed 's/^/  /'
echo ""
echo "=== 배포된 stuck_monitor.py 에 억제 로직이 있는가 ==="
grep -nE "recovery_until|cb_behavior|_action/status" ~/ros2_ws/install/rover_bringup/lib/rover_bringup/stuck_monitor.py 2>/dev/null | sed 's/^/  /'
