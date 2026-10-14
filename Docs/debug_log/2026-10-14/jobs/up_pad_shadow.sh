#!/bin/bash
# (10-14 §19) 실행 중인 pad_relief 를 관찰 모드(shadow)로 다시 띄움 — 패딩은 바꾸지 않고 판정·기록만. 로버 안 움직임
pkill -f "python3 -u /tmp/pad_relief.py" 2>/dev/null; sleep 1
export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "--- 기존 기록"; cut -d' ' -f2- /tmp/pad_relief.log | tail -3; mv /tmp/pad_relief.log /tmp/pad_relief_f2t1.log
setsid nohup python3 -u /tmp/pad_relief.py --ros-args -p mode:=shadow > /tmp/pad_relief_node.log 2>&1 < /dev/null &
for i in 1 2 3 4 5 6 7 8; do sleep 1; grep -q "원래 패딩" /tmp/pad_relief.log 2>/dev/null && break; done
echo "--- 새 기록"; cut -d' ' -f2- /tmp/pad_relief.log; echo "실행 $(pgrep -fc 'python3 -u /tmp/pad_relief.py') 개 · 로컬 패딩 $(timeout 10 ros2 param get /local_costmap/local_costmap footprint_padding 2>&1 | tail -1)"
