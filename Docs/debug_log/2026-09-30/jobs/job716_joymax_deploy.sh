#!/bin/bash
# 09-30 §15: 조이스틱 mapping 프로필을 펌웨어 상한(0.085 m/s·0.38 rad/s)으로 — src 배포·빌드, 실행 중 teleop 파라미터도 즉시 변경
cp /tmp/joy_teleop.launch.py ~/ros2_ws/src/rover_bringup/launch/joy_teleop.launch.py
cp /tmp/joy_teleop.yaml ~/ros2_ws/src/rover_bringup/config/joy_teleop.yaml
cd ~/ros2_ws && colcon build --packages-select rover_bringup 2>&1 | tail -1; source install/setup.bash
grep -n "_PROFILES = " install/rover_bringup/share/rover_bringup/launch/joy_teleop.launch.py
if pgrep -f teleop_node >/dev/null; then
  timeout 8 ros2 param set /teleop_twist_joy_node scale_linear.x 0.085
  timeout 8 ros2 param set /teleop_twist_joy_node scale_angular.yaw 0.38
  echo "실행 중 teleop: x=$(timeout 8 ros2 param get /teleop_twist_joy_node scale_linear.x) | yaw=$(timeout 8 ros2 param get /teleop_twist_joy_node scale_angular.yaw)"
else echo "teleop 미실행 — 다음 기동부터 반영"; fi
