#!/bin/bash
# 09-30 §5: 브리지를 viz:=map 으로 교체(다른 스택 유지) — 빌드 → 기존 브리지 종료 → 새로 기동 → 설정 확인
set +u; cd ~/ros2_ws && colcon build --packages-select rover_bringup 2>&1 | tail -1; source install/setup.bash
export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml
pkill -INT -f foxglove_bridge; sleep 3; pkill -9 -f foxglove_bridge 2>/dev/null
setsid nohup ros2 launch rover_bringup foxglove.launch.py viz:=map > /tmp/foxglove_map.log 2>&1 < /dev/null &
sleep 6
echo "  브리지 프로세스: $(pgrep -fc 'lib/foxglove_bridge/foxglove_bridge')"
echo "  capabilities: $(timeout 8 ros2 param get /foxglove_bridge capabilities 2>&1 | tail -1)"
echo "  topic_whitelist: $(timeout 8 ros2 param get /foxglove_bridge max_qos_depth 2>&1 | tail -1)"; echo "  whitelist: $(timeout 8 ros2 param get /foxglove_bridge topic_whitelist 2>&1 | tail -1)"
