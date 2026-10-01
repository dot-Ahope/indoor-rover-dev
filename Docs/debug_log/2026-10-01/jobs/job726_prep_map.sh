#!/bin/bash
# 10-01 §5: 지도 불러오기 prep — 기본 office_v2(출발 테이프 = 0,0,0). 인자/환경:
#   MAP=office_v2|office_v1   MAPPING=1(매핑 전용·조종 기동) | 0(Nav2 포함, 기본)
#   ⚠ 이어 그리기 매핑이면 루프 클로저 끔 권장(10-01 §2: 켜면 옛 지도를 다시 최적화해 옮김) — 아직 slam.yaml 기본은 켬, 필요 시 SLAM_EXTRA_ARGS 로
set +u; MAP=${MAP:-office_v2}; M=${MAPPING:-0}
[ -e /home/jetson/maps/office/$MAP.posegraph ] || { echo "지도 없음: $MAP"; exit 1; }
echo "== 지도 $MAP | 매핑 전용 $M | SLAM 루프 창: $(grep -aoE 'loop_search_space_dimension: [0-9.]+' ~/ros2_ws/install/rover_bringup/share/rover_bringup/config/slam.yaml)"
MAPPING=$M SLAM_ARGS="map_file:=/home/jetson/maps/office/$MAP" SENSORS_ARGS="viz:=map" bash /tmp/job240_clean.sh 15 2>&1 | grep -av "^   [0-9]\.[0-9]0 " | head -80
if [ "$M" = "1" ]; then echo "== 조이스틱 재기동"; bash /tmp/job685_f1_teleop.sh; fi
echo "== slam 불러오기: $(grep -a 'Load From File\|load' /tmp/slam.log | head -2)"
echo "== 프로세스"; for p in rplidar realsense2_camera ekf_node async_slam_toolbox stuck_monitor foxglove_bridge controller_server "ros2 bag record" teleop_node; do printf "  %-20s %s\n" "$p" "$(pgrep -fc "$p")"; done
