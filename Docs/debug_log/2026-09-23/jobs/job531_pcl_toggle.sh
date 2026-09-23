#!/bin/bash
# N6-2 C1 정지 A/B: 모드 N 에서 realsense 점군 생성 끄기 — CPU(realsense·릴레이·nvblox)·점군/깊이 Hz·nvblox 깊이 콜백 비교, 끝에 복구
set +u
export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
hz() { timeout 7 ros2 topic hz "$1" 2>&1 | grep -ao 'average rate: [0-9.]*' | head -1 | cut -d' ' -f3; }
meas() {
  echo "  점군 Hz: ${1:-}$(hz /camera/camera/depth/color/points) | 깊이 Hz: $(hz /camera/camera/depth/image_rect_raw) | 릴레이 출력 Hz: $(hz /camera/depth/points_filtered)"
  top -b -n2 -d10 2>/dev/null | awk '/PID +USER/{f++} f==2 && $9+0>0.5 {print $1, $9, $NF}' > /tmp/top531.txt
  echo -n "  CPU 20 s: "; while read pid cpu cmd; do nm=$cmd; [ "$cmd" = python3 ] && nm=$(ps -o args= -p $pid 2>/dev/null | grep -aoE 'depth_relay|sensor_conditioner|stuck_monitor|job[0-9]+' | head -1); case "$nm" in realsense*|depth_relay|sensor_conditioner|nvblox*|controller*|planner*) printf "%s %s%% | " "$nm" "$cpu";; esac; done < /tmp/top531.txt; echo
  echo "  top 상위(>3%): $(awk '$2+0>3 {printf "%s=%s ", $3, $2}' /tmp/top531.txt)"
  echo "  nvblox 깊이 콜백: $(grep -aA7 'NVBlox Rates' /tmp/nvblox_node.log | grep -aE 'ros/depth_image_callback' | awk '{print $NF}' | tail -1) Hz | 전체 합(top): $(awk '{s+=$2} END {printf "%.0f", s}' /tmp/top531.txt) %"
}
echo "## 현재 점군 파라미터: $(timeout 12 ros2 param get /camera/camera pointcloud.enable 2>&1 | tail -1) / neon: $(timeout 12 ros2 param get /camera/camera pointcloud__neon_.enable 2>&1 | tail -1)"
echo "## A. 점군 켬(현재)"; meas
echo "## B. pointcloud__neon_.enable false"; timeout 15 ros2 param set /camera/camera pointcloud__neon_.enable false 2>&1 | tail -1; sleep 6; meas
echo "## C. 복구 true"; timeout 15 ros2 param set /camera/camera pointcloud__neon_.enable true 2>&1 | tail -1; sleep 6; meas
