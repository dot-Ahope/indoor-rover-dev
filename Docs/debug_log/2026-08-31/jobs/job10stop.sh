#!/bin/bash
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "===즉시 종료: 모든 joy/teleop/launch==="
pkill -9 -f teleop 2>/dev/null; pkill -9 -f joy_linux 2>/dev/null; pkill -9 -f joy_node 2>/dev/null; pkill -9 -f joy_teleop 2>/dev/null; sleep 2
echo "잔존: teleop $(pgrep -f teleop|wc -l), joy $(pgrep -f 'joy_linux|joy_node'|wc -l), launch $(pgrep -f joy_teleop|wc -l)"
echo "===명시 정지 발행==="
timeout 3 ros2 topic pub -t 15 -r 10 -w 1 /cmd_vel geometry_msgs/msg/Twist '{}' >/dev/null 2>&1 && echo "정지 발행됨"
echo "===로버 실제 정지 확인==="
timeout 5 ros2 topic echo /odometry/filtered --once --field twist.twist 2>/dev/null | grep -E "^  x:|^  z:" | head -2
echo -n "cmd_vel 현재값: "; timeout 4 ros2 topic echo /cmd_vel --once 2>/dev/null | grep -A1 linear | grep "x:" | head -1 || echo "무발행(정상)"
