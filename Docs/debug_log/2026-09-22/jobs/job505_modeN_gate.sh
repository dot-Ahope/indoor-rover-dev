#!/bin/bash
# 절차 v2.0 게이트 J·K·L (모드 N 전용, 09-22): nvblox 노드 1 개·깊이 ≥10 Hz·ESDF ≥9 Hz·지연 ≤0.15 s, 로컬 plugins 실효값 = nvblox_layer, 슬라이스 상자 커버(≥0 셀 ≥8 — 09-22 정정: 절단 2.0 기하 4×2~3 셀, 처음 10 은 n4n2 배치에서 9 로 근소 불합격)·근거리 자취 0.
#   인자: LOGNAME BX BY   (LOGNAME = nvblox 시작 때 쓴 이름, 로그 /tmp/nvblox_<LOGNAME>.log). 주행 30 s 전에 끝낼 것(DDS 참여자 생성).
set +u
NM=${1:-n4}; BX=$2; BY=$3; CN=isaac_ros_dev-aarch64-container; BIN=/opt/ros/humble/lib/nvblox_ros/nvblox_node
export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
NP=$(docker exec $CN bash -c "pgrep -fc '^$BIN' || true")
R_D=$(grep -aA7 "NVBlox Rates" /tmp/nvblox_$NM.log | grep -aE "ros/depth_image_callback" | awk '{print $NF}' | tail -1)
R_E=$(grep -aA7 "NVBlox Rates" /tmp/nvblox_$NM.log | grep -aE "ros/update_esdf" | awk '{print $NF}' | tail -1)
D_E=$(grep -aA7 "NVBlox Delays" /tmp/nvblox_$NM.log | grep -aE "esdf_integration" | awk '{print $NF}' | tail -1)
J=$(awk -v n="$NP" -v d="$R_D" -v e="$R_E" -v l="$D_E" 'BEGIN{print (n==1 && d+0>=10 && e+0>=9 && l+0<=0.15) ? "통과" : "불합격"}')
echo "J nvblox 노드: 프로세스 $NP, 깊이 ${R_D:-?} Hz, ESDF ${R_E:-?} Hz, esdf 지연 ${D_E:-?} s → $J"
PL=$(timeout 12 ros2 param get /local_costmap/local_costmap plugins 2>&1 | tail -1)
K=$(echo "$PL" | grep -q nvblox_layer && echo 통과 || echo 불합격); echo "K 층 실효값: $(echo $PL | cut -c1-70) → $K"
OUT=$(docker exec -u admin --workdir /workspaces/isaac_ros-dev $CN bash -lc "export FASTRTPS_DEFAULT_PROFILES_FILE=/tmp/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; python3 /tmp/job474_n0_measure.py gate 8 $BX $BY /nvblox_node/static_map_slice 2>&1 | grep -av '^\['")
CELLS=$(echo "$OUT" | grep -ao '프레임당 셀 [0-9]*' | grep -ao '[0-9]*$'); NEAR=$(echo "$OUT" | grep -ao '0 이 아닌 프레임 [0-9]*' | grep -ao '[0-9]*$'); FR=$(echo "$OUT" | grep -ao '슬라이스 [0-9]* 프레임' | grep -ao '[0-9]*')
L=$(awk -v c="$CELLS" -v n="$NEAR" -v f="$FR" 'BEGIN{print (c+0>=8 && n+0==0 && f+0>=30) ? "통과" : "불합격"}')
echo "L 슬라이스 커버: 상자 띠 셀/프레임 ${CELLS:-?}, 근거리 자취 프레임 ${NEAR:-?}/${FR:-?} → $L"; echo "$OUT" | grep -aE "\(i\)|\(ii\)|\(iii\)" | cut -c1-150
[ "$J" = 통과 ] && [ "$K" = 통과 ] && [ "$L" = 통과 ] && echo "== 모드 N 게이트 J·K·L 통과" || { echo "== 모드 N 게이트 불합격 — 주행하지 않음"; exit 1; }
