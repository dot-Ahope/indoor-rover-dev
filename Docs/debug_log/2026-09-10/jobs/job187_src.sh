#!/bin/bash
echo "=== 배포된 stuck_monitor.py 88~140행 ==="
sed -n '88,140p' ~/ros2_ws/install/rover_bringup/lib/rover_bringup/stuck_monitor.py | cat -n | sed 's/^/  /'
echo ""
echo "=== import 확인 ==="
grep -nE "^from|^import" ~/ros2_ws/install/rover_bringup/lib/rover_bringup/stuck_monitor.py | sed 's/^/  /'
