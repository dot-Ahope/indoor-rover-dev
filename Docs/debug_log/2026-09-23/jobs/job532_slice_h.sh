#!/bin/bash
# N6-2 H1 정지 측정(Jetson): 슬라이스 최소 높이 0.03 vs 0.06(통합 1.4 고정). 변형 yaml 을 설치본 위에 잠시 덮고 Nav2(nvblox) 재기동 → 3 표본(게이트 L 상자 셀·목표 부근 유령·상자 왼쪽 가장자리 차) → 원본 복구·재기동. 인자: BX BY
set +u
BX=$1; BY=$2
export TERM=xterm FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
Y=~/ros2_ws/install/rover_navigation/share/rover_navigation/config/nvblox_local.yaml
cp -f $Y /tmp/nvblox_local.orig.yaml
sample() {   # 이름
  local NM=$1 i
  echo "## $NM: 슬라이스 min $(grep -ao 'esdf_slice_min_height: [0-9.]*' /tmp/nvblox_active.yaml | grep -ao '[0-9.]*$') 실효 $(docker exec -u admin isaac_ros_dev-aarch64-container bash -lc 'export FASTRTPS_DEFAULT_PROFILES_FILE=/tmp/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; timeout 12 ros2 param get /nvblox_node static_mapper.esdf_slice_min_height 2>&1 | tail -1 | sed "s/Double value is: //"')"
  for i in 1 2 3; do
    L=$(docker exec -u admin --workdir /workspaces/isaac_ros-dev isaac_ros_dev-aarch64-container bash -lc "export FASTRTPS_DEFAULT_PROFILES_FILE=/tmp/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; python3 /tmp/job474_n0_measure.py h 6 $BX $BY /nvblox_node/static_map_slice 2>&1" | grep -ao '프레임당 셀 [0-9]*' | grep -ao '[0-9]*$')
    PR=$(python3 /tmp/job522_goalprobe.py 2>&1 | grep -av '^\['); GL=$(echo "$PR" | grep -a '전역 코스트맵' | grep -ao 'LETHAL(100) [0-9]*' | grep -ao '[0-9]*$'); SL=$(echo "$PR" | grep -a 'nvblox 슬라이스' | grep -ao '≤0(장애물) [0-9]*' | grep -ao '[0-9]*$')
    BY3=$(timeout 60 python3 /tmp/job315_boxcells.py 2>&1 | grep -aoE '^[-+]?[0-9.]+$' | tail -1)
    echo "  표본 $i: 상자 셀/프레임 ${L:-?} | 목표 부근 슬라이스 ≤0 ${SL:-?} · 전역 LETHAL ${GL:-?} | 코스트맵 상자 최대 y ${BY3:-?}"
    sleep 8
  done
  echo "  카메라 상자 y 구간: $(BOX_HINT="$BX $BY" timeout 100 python3 /tmp/job248_audit.py 2>&1 | grep -ao 'y 구간 \[[-+0-9.]*, [-+0-9.]*\]' | head -1)"
}
echo "######## 기준(현재 설치본 0.06)"; sample h06
echo "######## 변형 0.03"; sed -e 's/esdf_slice_min_height: 0.06.*/esdf_slice_min_height: 0.03   # H1 시험 변형/' -e 's/esdf_slice_height: 0.10.*/esdf_slice_height: 0.10/' /tmp/nvblox_local.orig.yaml > $Y
QUICK=1 bash /tmp/job488_layer_ab.sh nvblox $BX $BY 2>&1 | grep -aE '실행값|오류'; sleep 40; sample h03
echo "######## 복구 0.06"; cp -f /tmp/nvblox_local.orig.yaml $Y; QUICK=1 bash /tmp/job488_layer_ab.sh nvblox $BX $BY 2>&1 | grep -aE '실행값|오류'; sleep 35
echo "  복구 실효 min: $(docker exec -u admin isaac_ros_dev-aarch64-container bash -lc 'export FASTRTPS_DEFAULT_PROFILES_FILE=/tmp/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; timeout 12 ros2 param get /nvblox_node static_mapper.esdf_slice_min_height 2>&1 | tail -1')"
