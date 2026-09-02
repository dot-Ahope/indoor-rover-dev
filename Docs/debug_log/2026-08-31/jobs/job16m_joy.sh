#!/bin/bash
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
ls /dev/input/js0 >/dev/null 2>&1 || echo "js0 없음! USB 재연결 필요"
pkill -f joy_linux; pkill -f teleop_twist_joy; sleep 2
setsid nohup ros2 launch rover_bringup joy_teleop.launch.py > /tmp/joy.log 2>&1 &
sleep 6
echo "노드: $(ros2 node list 2>/dev/null | grep -E 'joy|teleop' | tr '\n' ' ')"
echo "=== /joy 중립 확인 ==="; timeout 4 ros2 topic echo /joy --once 2>/dev/null | grep -aA2 "axes" | head -4 || echo "  (스틱 살짝 움직이면 나옴)"
echo -n "=== /cmd_vel (중립=0): "; timeout 3 ros2 topic echo /cmd_vel --once 2>/dev/null | grep -aE "x:|z:" | head -2 || echo "무발행(정상)"
echo "  load: $(cat /proc/loadavg | cut -d' ' -f1-3)"
echo "완료 — 주행 가능"
