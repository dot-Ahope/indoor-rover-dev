#!/bin/bash
source /opt/ros/humble/setup.bash 2>/dev/null
echo "=== joy/teleop 정리 (cmd_vel 이중발행 제거) ==="
pkill -f joy_linux; pkill -f teleop_twist_joy; sleep 1; echo "  joy 종료"
echo "=== 코어 수 / load ==="
echo "  nproc=$(nproc), loadavg=$(cat /proc/loadavg)"
echo "=== 프로세스별 CPU (2프레임, 상위) ==="
top -b -n 2 -d 1 -o %CPU | awk '/PID +USER/{f++} f==2' | head -16
