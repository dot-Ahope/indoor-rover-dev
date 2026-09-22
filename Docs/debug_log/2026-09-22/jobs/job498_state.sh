#!/bin/bash
# 09-22 시작 상태(읽기 전용): 재부팅 여부, /tmp 스크립트 잔존, 스택 프로세스, 컨테이너, 로컬 plugins, nvblox 포크 diff
echo "== uptime: $(uptime -p) | 부팅: $(uptime -s)"
echo "== /tmp 스크립트: $(ls /tmp/job*.sh /tmp/job*.py /tmp/*.yaml 2>/dev/null | wc -l) 개 (job473 $(test -f /tmp/job473_nvblox_run.sh && echo 있음 || echo 없음), job489 $(test -f /tmp/job489_gridcmp.py && echo 있음 || echo 없음), job248 $(test -f /tmp/job248_audit.py && echo 있음 || echo 없음), job478 $(test -f /tmp/job478_boxphys.py && echo 있음 || echo 없음), nvblox_n0.yaml $(test -f /tmp/nvblox_n0.yaml && echo 있음 || echo 없음))"
echo "== 스택: agent $(docker ps --format '{{.Names}}' | grep -c micro) sensors(camera) $(pgrep -fc realsense2_camera_node) relay $(pgrep -fc depth_relay) slam $(pgrep -fc slam_toolbox) ekf $(pgrep -fc ekf_node) controller $(pgrep -fc controller_server) planner $(pgrep -fc planner_server) rsp $(pgrep -fc robot_state_publisher)"
echo "== 컨테이너: $(docker ps --format '{{.Names}} {{.Status}}' | grep isaac || echo 없음) | nvblox 프로세스 $(docker exec isaac_ros_dev-aarch64-container ps -eo cmd 2>/dev/null | grep -ac 'nvblox_nod[e]')"
echo "== 포크 diff: $(git -C /home/jetson/workspaces/isaac_ros-dev/src/isaac_ros_nvblox --no-pager diff --stat 2>/dev/null | tail -1)"
export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; source /home/jetson/ros2_ws/install/setup.bash
echo "== 로컬 plugins: $(timeout 12 ros2 param get /local_costmap/local_costmap plugins 2>&1 | tail -1 | cut -c1-90)"
echo "== 토픽 Hz(5 s): scan $(timeout 6 ros2 topic hz /scan 2>&1 | grep -ao 'average rate: [0-9.]*' | head -1 | cut -d' ' -f3) | depth $(timeout 6 ros2 topic hz /camera/camera/depth/image_rect_raw 2>&1 | grep -ao 'average rate: [0-9.]*' | head -1 | cut -d' ' -f3) | wheel_odom $(timeout 6 ros2 topic hz /wheel_odom 2>&1 | grep -ao 'average rate: [0-9.]*' | head -1 | cut -d' ' -f3)"
echo "== 로드: $(cut -d' ' -f1-3 /proc/loadavg) | 온도 $(awk '{printf "%.1f", $1/1000}' /sys/devices/virtual/thermal/thermal_zone0/temp) °C | 디스크 $(df -h / | awk 'NR==2{print $4" 남음"}')"
