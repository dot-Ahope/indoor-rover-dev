#!/bin/bash
# Jetson 측 파일(ssh 인라인에 프로세스 이름을 두지 않기 위해): 마감 상태 읽기 전용 확인
echo "== 컨테이너 nvblox 프로세스: $(docker exec isaac_ros_dev-aarch64-container ps -eo pid,etimes,cmd 2>/dev/null | grep -a 'nvblox_nod[e]' | wc -l) 개"
docker exec isaac_ros_dev-aarch64-container ps -eo pid,etimes,cmd 2>/dev/null | grep -a 'nvblox_nod[e]' | cut -c1-100
echo "== 호스트 nvblox 관련 프로세스: $(pgrep -fc 'nvblox_nod[e]')"
export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; source /home/jetson/ros2_ws/install/setup.bash
echo "== 로컬 plugins: $(timeout 12 ros2 param get /local_costmap/local_costmap plugins 2>&1 | tail -1 | cut -c1-90)"
echo "== 스택 프로세스: controller $(pgrep -fc controller_server) planner $(pgrep -fc planner_server) slam $(pgrep -fc slam_toolbox) relay $(pgrep -fc depth_relay) agent $(docker ps --format '{{.Names}}' | grep -c micro)"
echo "== 로드: $(cut -d' ' -f1-3 /proc/loadavg) | 온도: $(cat /sys/devices/virtual/thermal/thermal_zone0/temp 2>/dev/null | awk '{printf "%.1f", $1/1000}') °C"
