#!/bin/bash
# 09-30 §16: 매핑 재시작 — office_v1 불러오기(출발 테이프 = 0,0,0), 매핑 전용 모드, 루프 창 3 m, bag 자동, stuck 관찰, Foxglove map 세트
set +u
echo "== 배포된 SLAM 루프 창: $(grep -aoE 'loop_search_space_dimension: [0-9.]+' ~/ros2_ws/install/rover_bringup/share/rover_bringup/config/slam.yaml)"
MAPPING=1 SLAM_ARGS="map_file:=/home/jetson/maps/office/office_v1" SENSORS_ARGS="viz:=map" bash /tmp/job240_clean.sh 15 2>&1 | grep -av "^   [0-9]\.[0-9]0 " | head -70
echo "== 조이스틱 재기동(prep 이 joy 노드를 정리하므로)"
bash /tmp/job685_f1_teleop.sh
echo "== 프로세스"; for p in rplidar realsense2_camera ekf_node async_slam_toolbox stuck_monitor foxglove_bridge "ros2 bag record" teleop_node; do printf "  %-20s %s\n" "$p" "$(pgrep -fc "$p")"; done
echo "== bag: $(ls -d /tmp/bags/map_* 2>/dev/null | tail -1)"
