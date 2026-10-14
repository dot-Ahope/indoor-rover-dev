#!/bin/bash
# (10-14 §9) f2r1 뒤: pad_relief 기록·컨트롤러 실패 로그·현재 패딩 확인 — 로버 안 움직임
echo "--- pad_relief.log"; cut -d" " -f2- /tmp/pad_relief.log
echo "--- Nav2 로그의 컨트롤러 실패(11:23:29 이후)"; S0=$(date -d 11:23:29 +%s); grep -a -o "\[\(ERROR\|WARN\)\] \[[0-9]*\.[0-9]*\] \[[a-z_.]*\]: .\{0,70\}" /tmp/nav2.log | awk -v a=$S0 '{t=$2; gsub(/[\[\]]/,"",t); if (t+0>=a) {printf "%s ", strftime("%H:%M:%S", t); $2=""; print}}' | grep -a "fail to compute\|collision\|Collision\|backup\|Goal failed\|Aborting" | head -40
echo "--- 실패 문구 수: $(grep -ac "fail to compute path" /tmp/nav2.log)"
export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash
echo "현재 로컬 패딩: $(timeout 12 ros2 param get /local_costmap/local_costmap footprint_padding 2>&1 | tail -1) · pad_relief $(pgrep -fc "python3 -u /tmp/pad_relief.py") 개"
