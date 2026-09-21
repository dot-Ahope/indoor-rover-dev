#!/bin/bash
# N0 (iv)+입력 해상도 변형, 2 차 (2026-09-21): 1 차(job481)는 재시작한 노드가 깊이 1 프레임 뒤 멈추고 죽어 0 프레임. 원인 후보: pkill -f 가 자기 bash 를 먼저 죽여 옛 노드가 남음·확인 없이 측정.
#   이번엔 정확한 실행 파일 경로로 PID 를 찾아 죽이고, 사라진 것을 확인한 뒤 시작, 30 s 뒤 통계 블록에서 깊이 콜백 ≥ 10 Hz 를 확인하고서야 측정. 실패하면 로그 꼬리를 남기고 다음으로.
# 인자: BX BY
set +u
BX=$1; BY=$2; CN=isaac_ros_dev-aarch64-container; BIN=/opt/ros/humble/lib/nvblox_ros/nvblox_node
export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
nv_pids() { docker exec $CN bash -c "pgrep -f '^$BIN' || true"; }
nv_stop() { local p; for p in $(nv_pids); do docker exec $CN kill -INT $p 2>/dev/null; done; sleep 3; for p in $(nv_pids); do docker exec $CN kill -9 $p 2>/dev/null; done; sleep 1; echo "  정지 후 nvblox pid: '$(nv_pids | tr '\n' ' ')'"; }
nv_start() { local Y=$1 NM=$2; docker exec -d -u admin --workdir /workspaces/isaac_ros-dev $CN bash -lc "export FASTRTPS_DEFAULT_PROFILES_FILE=/tmp/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; exec ros2 run nvblox_ros nvblox_node --ros-args --params-file /tmp/$Y -r camera_0/depth/image:=/camera/camera/depth/image_rect_raw -r camera_0/depth/camera_info:=/camera/camera/depth/camera_info > /tmp/nvblox_$NM.log 2>&1"; }
depth_rate() { grep -aA7 "NVBlox Rates" /tmp/nvblox_$1.log | grep -aE "ros/depth_image_callback" | awk '{print $NF}' | tail -1; }   # 2 차 실수: Rates 블록 뒤 Delays 블록의 같은 이름 줄(0.064 s)을 읽어 '안 받음' 으로 오판 → Rates 헤더 뒤 7 줄만
run_variant() {   # 이름 yaml dec
  local NM=$1 Y=$2 DEC=$3
  echo "######## $NM (yaml $Y, dec $DEC)"
  timeout 10 ros2 param set /camera/camera decimation_filter.filter_magnitude $DEC 2>&1 | tail -1; sleep 4
  echo "  깊이 이미지: $(timeout 6 ros2 topic echo /camera/camera/depth/image_rect_raw --once --field width 2>/dev/null | head -1)x$(timeout 6 ros2 topic echo /camera/camera/depth/image_rect_raw --once --field height 2>/dev/null | head -1) @ $(timeout 8 ros2 topic hz /camera/camera/depth/image_rect_raw 2>&1 | grep -ao 'average rate: [0-9.]*' | head -1)"
  nv_stop; nv_start $Y $NM; sleep 32
  local R=$(depth_rate $NM); echo "  30 s 뒤 깊이 콜백 rate: ${R:-없음} (pid $(nv_pids | tr '\n' ' '))"
  if ! awk -v r="$R" 'BEGIN{exit !(r+0 >= 10)}'; then echo "  ★ 노드가 깊이를 안 받음 — 로그 꼬리:"; tail -6 /tmp/nvblox_$NM.log | cut -c1-160; return; fi
  docker exec -u admin --workdir /workspaces/isaac_ros-dev $CN bash -lc "export FASTRTPS_DEFAULT_PROFILES_FILE=/tmp/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; python3 /tmp/job474_n0_measure.py $NM 20 $BX $BY /nvblox_node/static_map_slice 2>&1 | grep -av '^\['" &
  sleep 6; timeout 6 tegrastats --interval 1000 2>/dev/null | awk '{for(i=1;i<=NF;i++) if($i ~ /GR3D_FREQ/) g=$(i+1); if(match($0,/CPU \[[^]]*\]/)) c=substr($0,RSTART,RLENGTH); print "  tegra GPU " g " " c}' | tail -3
  echo "  nvblox CPU(top): $(top -b -n2 -d2 2>/dev/null | awk '/PID +USER/{f++} f==2' | awk '$12 ~ /nvblox/ {printf "%s%% ", $9}')"
  wait
  grep -aA7 "NVBlox Rates" /tmp/nvblox_$NM.log | tail -7 | grep -aE "ros/depth |ros/update_esdf|ros/depth_image_callback" | sed 's/^/  rate /' | cut -c1-80
  grep -aA7 "NVBlox Delays" /tmp/nvblox_$NM.log | tail -7 | grep -aE "esdf_integration|depth_image_callback" | sed 's/^/  delay /' | cut -c1-80
  grep -aE "^tsdf/integrate |^ros/esdf/integrate " /tmp/nvblox_$NM.log | tail -2 | awk '{printf "  time %s mean %.2f ms\n", $1, $3*1000/$2}'
}
run_variant v03_dec4 nvblox_n0_v03.yaml 4
run_variant v05_dec2 nvblox_n0.yaml 2
run_variant v05_dec1 nvblox_n0.yaml 1
echo "######## 복귀: dec 4, 복셀 0.05"; run_variant v05_dec4 nvblox_n0.yaml 4
