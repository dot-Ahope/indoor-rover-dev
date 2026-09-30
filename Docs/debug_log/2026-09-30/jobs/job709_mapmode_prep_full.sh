#!/bin/bash
# 09-30 §11: 매핑 모드 prep 전체 출력(원인 확인)
set +u
MAPPING=1 SLAM_ARGS="map_file:=/home/jetson/maps/office/office_v1" SENSORS_ARGS="viz:=map" bash /tmp/job240_clean.sh 15 2>&1 | grep -av "^   [0-9]\.[0-9]0 " | head -70
echo "== 끝난 뒤 프로세스"; for p in rplidar realsense2_camera ekf_node async_slam_toolbox stuck_monitor foxglove_bridge; do printf "  %-20s %s
" $p "$(pgrep -fc $p)"; done
