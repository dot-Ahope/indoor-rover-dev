#!/bin/bash
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo -n "  agent: "; docker ps --format '{{.Names}} {{.Status}}' | grep microros || echo "없음"
echo -n "  /wheel_odom: "; timeout 6 ros2 topic hz /wheel_odom 2>&1 | grep -aoE "average rate: [0-9.]+" | head -1 || echo "무발행"
echo -n "  보드 노드: "; ros2 node list 2>/dev/null | grep rover_jupiter || echo "없음"
