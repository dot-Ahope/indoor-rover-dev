#!/bin/bash
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "===agent 컨테이너(리셋 시 재연결에 필요)==="
docker ps --format '{{.Names}} {{.Status}}' | grep microros || echo "❌ NO_AGENT (base.launch 재시작 필요)"
echo "===현재 세션(리셋 전)==="
echo -n "  wheel_odom: "; timeout 5 ros2 topic hz /wheel_odom 2>&1 | grep -aE "average|does not" | tail -1
echo "===주요 노드==="
ros2 node list | grep -E "rover_jupiter|ekf|slam|scan_deskew|rplidar|camera|robot_state" | tr '\n' ' '; echo
echo "===teleop 잔존(정리)==="
pkill -9 -f teleop 2>/dev/null; pkill -9 -f joy_linux 2>/dev/null; echo "teleop/joy 정리됨"
