#!/bin/bash
# 10-01 §5·§7: 지도 불러오기 prep — 기본 office_v3(10-02 §4, 이전 office_v2)(출발 테이프 = 0,0,0). 인자/환경:
#   MAP=office_v2|office_v1   MAPPING=1(매핑 전용·조종 기동) | 0(Nav2 포함, 기본)
#   LOC=map(기본: slam_toolbox 이어 그리기) | slamloc(slam_toolbox 위치 추정, 지도 고정) | amcl(map_server+AMCL, 격자 지도)
#   ⚠ 이어 그리기 매핑이면 루프 클로저 끔 권장(10-01 §2: 켜면 옛 지도를 다시 최적화해 옮김)
set +u; MAP=${MAP:-office_v3}; M=${MAPPING:-0}; L=${LOC:-map}; D=/home/jetson/maps/office
[ -e $D/$MAP.posegraph ] || { echo "지도 없음: $MAP"; exit 1; }
case "$L" in
  map)     export LOCALIZER=slam; SA="map_file:=$D/$MAP" ;;
  slamloc) export LOCALIZER=slam; SA="map_file:=$D/$MAP slam_mode:=localization"; export NAV_ARGS="nav_map:=$D/$MAP.yaml" ;;   # 10-01 §8.33 전역 정적 층 = 저장 지도
  amcl)    export LOCALIZER=amcl AMCL_MAP=$D/$MAP.yaml; SA="" ;;
  *) echo "LOC 는 map|slamloc|amcl"; exit 1 ;;
esac
echo "== 지도 $MAP | 위치 추정 $L | 매핑 전용 $M | SLAM 루프 창: $(grep -aoE 'loop_search_space_dimension: [0-9.]+' ~/ros2_ws/install/rover_bringup/share/rover_bringup/config/slam.yaml)"
MAPPING=$M SLAM_ARGS="$SA" SENSORS_ARGS="viz:=map" bash /tmp/job240_clean.sh 15 2>&1 | grep -av "^   [0-9]\.[0-9]0 " | head -80
if [ "$M" = "1" ]; then echo "== 조이스틱 재기동"; bash /tmp/job685_f1_teleop.sh; fi
echo "== 위치 추정 로그: $(grep -aE 'Load From File|위치 추정|이어 그리기|Setting pose|initialPose|Managed nodes are active|error|Error' /tmp/slam.log | head -4 | cut -c1-160)"
echo "== 프로세스"; for p in rplidar realsense2_camera ekf_node async_slam_toolbox localization_slam amcl map_server stuck_monitor foxglove_bridge controller_server "ros2 bag record" teleop_node; do printf "  %-20s %s\n" "$p" "$(pgrep -fc "$p")"; done
