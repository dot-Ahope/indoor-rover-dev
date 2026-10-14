#!/bin/bash
# (10-14 §9) pad_relief 만 다시 띄우고 상태 확인 — 로버 안 움직임
echo "이전 실패 원인: $(tail -3 /tmp/pad_relief_node.log 2>/dev/null | tr "
" " " | cut -c1-260)"
pkill -f "python3 -u /tmp/pad_relief.py" 2>/dev/null; rm -f /tmp/pad_relief.log
export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
setsid nohup python3 -u /tmp/pad_relief.py --ros-args -p mode:=on > /tmp/pad_relief_node.log 2>&1 < /dev/null &
for i in 1 2 3 4 5 6 7 8 9 10; do sleep 1; grep -q "원래 패딩" /tmp/pad_relief.log 2>/dev/null && break; done
echo "pad_relief: $(pgrep -fc "python3 -u /tmp/pad_relief.py") 개 실행 · $(cut -d" " -f2- /tmp/pad_relief.log 2>/dev/null | tr "
" "|" | cut -c1-220)"
