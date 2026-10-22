#!/bin/bash
# 10-22 §12 사용자 "그만 멈춰라" — 러너 · Nav2 주행 노드 종료 → 펌웨어 watchdog(cmd_vel 500 ms 무수신 정지) + 0 속도 발행
date +%T.%N | cut -c1-12
pkill -9 -f job551_f0drive.sh; pkill -9 -f job550_f0run.py
pkill -9 -f "nav2_controller/controller_server"; pkill -9 -f "nav2_bt_navigator/bt_navigator"; pkill -9 -f "nav2_behaviors/behavior_server"
source /opt/ros/humble/setup.bash
timeout 4 ros2 topic pub -r 10 -t 20 /cmd_vel geometry_msgs/msg/Twist "{}" >/dev/null 2>&1
date +%T.%N | cut -c1-12; echo "남은: 러너 $(pgrep -fc job550_f0run) · controller $(pgrep -fc controller_server) · bt $(pgrep -fc bt_navigator)"
