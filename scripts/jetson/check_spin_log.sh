#!/bin/bash
# 회전 로그 확인 + 프로세스 생존 여부 + 현재 상태
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "===spin.log 전체==="; cat /tmp/spin.log 2>/dev/null | grep -av "^$" || echo "(로그 없음)"
echo "===회전 프로세스 생존?==="; pgrep -af "map_spin" | cut -c1-70 || echo "종료됨(정상)"
echo "===현재 회전율==="; timeout 5 ros2 topic echo /odometry/filtered --once --field twist.twist.angular.z 2>/dev/null
echo "===맵 크기==="; timeout 5 ros2 topic echo /map --once --field info 2>/dev/null | grep -aE "width|height|resolution" | tr '\n' ' '; echo
echo "===uptime(재부팅 여부)==="; uptime | cut -c1-40
echo "===wheel_odom(세션)==="; timeout 5 ros2 topic hz /wheel_odom 2>&1 | grep -aE "average|does not" | tail -1
