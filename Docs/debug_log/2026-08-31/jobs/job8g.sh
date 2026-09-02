#!/bin/bash
# 회전 완료 대기 후 로그 읽기
for i in $(seq 1 15); do
  grep -qa SPIN_END /tmp/spin.log 2>/dev/null && break
  sleep 2
done
echo "===spin.log==="; cat /tmp/spin.log 2>/dev/null | grep -av "^$"
source /opt/ros/humble/setup.bash 2>/dev/null; source ~/ros2_ws/install/setup.bash 2>/dev/null
echo "===현재 회전율(정지 확인)==="; timeout 5 ros2 topic echo /odometry/filtered --once --field twist.twist.angular.z 2>/dev/null
