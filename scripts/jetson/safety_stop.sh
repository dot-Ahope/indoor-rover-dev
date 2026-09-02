#!/bin/bash
# 안전: 잔존 회전 프로세스 정리 + 정지 지령 + 현재 회전율 확인
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "===잔존 회전 프로세스==="
pgrep -af "map_spin|job7f|job7d|topic pub.*cmd_vel" | cut -c1-80 || echo "없음"
echo "===프로세스 종료==="
pkill -f "map_spin" 2>/dev/null; pkill -f "job7f" 2>/dev/null; pkill -f "job7d" 2>/dev/null; pkill -f "topic pub.*cmd_vel" 2>/dev/null
sleep 1
echo "===명시적 정지 지령 (안전) ==="
timeout 3 ros2 topic pub -t 8 -r 10 -w 1 /cmd_vel geometry_msgs/msg/Twist '{}' >/dev/null 2>&1 && echo "정지 지령 발행"
sleep 1
echo "===현재 회전율 (0이어야 정지) ==="
timeout 5 ros2 topic echo /odometry/filtered --once --field twist.twist.angular.z 2>/dev/null
echo "===현재 선속도==="
timeout 5 ros2 topic echo /odometry/filtered --once --field twist.twist.linear.x 2>/dev/null
echo "===cmd_vel 발행자 (없어야 정상)==="
timeout 4 ros2 topic echo /cmd_vel --once 2>/dev/null && echo "!! cmd_vel 계속 발행중" || echo "cmd_vel 무발행(정상)"
echo "===맵 현황==="
timeout 5 ros2 topic echo /map --once --field info 2>/dev/null | grep -aE "width|height" | tr '\n' ' '; echo
