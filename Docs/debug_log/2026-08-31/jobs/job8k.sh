#!/bin/bash
for i in $(seq 1 18); do grep -qa SPIN_END /tmp/spin.log 2>/dev/null && break; sleep 2; done
echo "===spin.log==="; cat /tmp/spin.log 2>/dev/null | grep -av "^$"
source /opt/ros/humble/setup.bash 2>/dev/null; source ~/ros2_ws/install/setup.bash 2>/dev/null
echo "===회전 중 slam 드롭 (queue full) 최근 수==="
grep -ac "dropping message" /tmp/slam.log 2>/dev/null
grep -a "dropping message" /tmp/slam.log 2>/dev/null | tail -2 | cut -c1-90
echo "===정지 확인==="; timeout 5 ros2 topic echo /odometry/filtered --once --field twist.twist.angular.z 2>/dev/null
echo "===맵 크기==="; timeout 5 ros2 topic echo /map --once --field info 2>/dev/null | grep -aE "width|height" | tr '\n' ' '; echo
