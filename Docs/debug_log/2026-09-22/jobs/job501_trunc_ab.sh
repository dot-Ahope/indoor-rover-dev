#!/bin/bash
# 09-22 §1 절단 거리 A/B (Jetson 측): 같은 배치에서 STVL 캡처 → nvblox 절단 4.0(t4) → 절단 2.0(t2) 순으로 로컬 코스트맵·슬라이스 JSON(job489)·감사(job248)·N0 계측(job474, 컨테이너)·GPU/CPU 를 얻는다.
#   층은 09-21 floor 수정본. nvblox 재시작은 job483 방식(실행 파일 경로 PID 로 정지, 깊이 콜백 ≥10 Hz 확인 후 측정). 인자: BX BY (base_link 기준 물리 상자 전면 x·중심 y, job478 출력)
#   끝나면 로컬 코스트맵을 STVL 로 되돌리고 nvblox 를 정지한다.
set +u
BX=$1; BY=$2; CN=isaac_ros_dev-aarch64-container; BIN=/opt/ros/humble/lib/nvblox_ros/nvblox_node
export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
nv_pids() { docker exec $CN bash -c "pgrep -f '^$BIN' || true"; }
nv_stop() { local p; for p in $(nv_pids); do docker exec $CN kill -INT $p 2>/dev/null; done; sleep 3; for p in $(nv_pids); do docker exec $CN kill -9 $p 2>/dev/null; done; sleep 1; echo "  정지 후 nvblox pid: '$(nv_pids | tr '\n' ' ')'"; }
nv_start() { local Y=$1 NM=$2; docker exec -d -u admin --workdir /workspaces/isaac_ros-dev $CN bash -lc "export FASTRTPS_DEFAULT_PROFILES_FILE=/tmp/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; exec ros2 run nvblox_ros nvblox_node --ros-args --params-file /tmp/$Y -r camera_0/depth/image:=/camera/camera/depth/image_rect_raw -r camera_0/depth/camera_info:=/camera/camera/depth/camera_info > /tmp/nvblox_$NM.log 2>&1"; }
depth_rate() { grep -aA7 "NVBlox Rates" /tmp/nvblox_$1.log | grep -aE "ros/depth_image_callback" | awk '{print $NF}' | tail -1; }
clear_cm() { timeout 10 ros2 service call /local_costmap/clear_entirely_local_costmap nav2_msgs/srv/ClearEntireCostmap "{}" >/dev/null 2>&1; sleep 12; }
audit3() { local i; for i in 1 2 3; do BOX_HINT="$BX $BY" timeout 100 python3 /tmp/job248_audit.py 2>&1 | grep -aE "^상자|로컬\[|최소폭|상자 셀" | head -4 | cut -c1-170; sleep 2; done; }
measure() {   # N0 계측(컨테이너 안 job474, 20 s) + GPU/CPU + nvblox 통계
  local NM=$1
  docker exec -u admin --workdir /workspaces/isaac_ros-dev $CN bash -lc "export FASTRTPS_DEFAULT_PROFILES_FILE=/tmp/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; python3 /tmp/job474_n0_measure.py $NM 20 $BX $BY /nvblox_node/static_map_slice 2>&1 | grep -av '^\['" &
  sleep 6; timeout 6 tegrastats --interval 1000 2>/dev/null | awk '{for(i=1;i<=NF;i++) if($i ~ /GR3D_FREQ/) g=$(i+1); if(match($0,/CPU \[[^]]*\]/)) c=substr($0,RSTART,RLENGTH); print "  tegra GPU " g " " c}' | tail -3
  echo "  CPU(top 2 회): $(top -b -n2 -d2 2>/dev/null | awk '/PID +USER/{f++} f==2' | awk '$12 ~ /nvblox|controller|planner|depth_relay/ {printf "%s %s%% | ", $12, $9}')"
  wait
  grep -aA7 "NVBlox Rates" /tmp/nvblox_$NM.log | tail -7 | grep -aE "ros/depth |ros/update_esdf|ros/depth_image_callback" | sed 's/^/  rate /' | cut -c1-80
  grep -aA7 "NVBlox Delays" /tmp/nvblox_$NM.log | tail -7 | grep -aE "esdf_integration|depth_image_callback" | sed 's/^/  delay /' | cut -c1-80
}
PHASE=${3:-a}   # a: STVL 캡처 + t4 / b: t2 + 복귀 (ssh 10 분 한도 때문에 둘로 나눔)
if [ "$PHASE" = a ]; then
echo "## 0. STVL 캡처(stvl3) — plugins: $(timeout 12 ros2 param get /local_costmap/local_costmap plugins 2>&1 | tail -1 | cut -c1-80)"
clear_cm; python3 /tmp/job489_gridcmp.py stvl3 0 2>&1 | grep -aE '^====|LETHAL 셀'
echo "## 1. t4 (nvblox_n0.yaml, 절단 4.0)"
nv_stop; nv_start nvblox_n0.yaml t4; sleep 32; R=$(depth_rate t4); echo "  30 s 뒤 깊이 콜백 rate: ${R:-없음} (pid $(nv_pids | tr '\n' ' '))"
if ! awk -v r="$R" 'BEGIN{exit !(r+0 >= 10)}'; then echo "  ★ t4 노드가 깊이를 안 받음 — 중단"; tail -6 /tmp/nvblox_t4.log | cut -c1-160; exit 2; fi
QUICK=1 bash /tmp/job488_layer_ab.sh nvblox $BX $BY 2>&1 | grep -aE '실행값|오류'
clear_cm; audit3 | tee /tmp/j501_ab_t4.txt
python3 /tmp/job489_gridcmp.py t4 1 2>&1 | grep -aE '^====|LETHAL 셀'; measure t4
echo "## (a 끝: nvblox t4 실행 중, 로컬 코스트맵 nvblox 모드 — b 단계로)"
exit 0
fi
echo "## 2. t2 (nvblox_n0_t2.yaml, 절단 2.0) — 현재 plugins: $(timeout 12 ros2 param get /local_costmap/local_costmap plugins 2>&1 | tail -1 | cut -c1-80)"
nv_stop; nv_start nvblox_n0_t2.yaml t2; sleep 32; R=$(depth_rate t2); echo "  30 s 뒤 깊이 콜백 rate: ${R:-없음} (pid $(nv_pids | tr '\n' ' '))"
if ! awk -v r="$R" 'BEGIN{exit !(r+0 >= 10)}'; then echo "  ★ t2 노드가 깊이를 안 받음 — 중단"; tail -6 /tmp/nvblox_t2.log | cut -c1-160; QUICK=1 bash /tmp/job488_layer_ab.sh stvl $BX $BY 2>&1 | grep -a 실행값; nv_stop; exit 2; fi
echo "  절단 파라미터 실효값: $(docker exec -u admin $CN bash -lc 'export FASTRTPS_DEFAULT_PROFILES_FILE=/tmp/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; timeout 12 ros2 param get /nvblox_node static_mapper.projective_integrator_truncation_distance_vox 2>&1 | tail -1')"
clear_cm; audit3 | tee /tmp/j501_ab_t2.txt
python3 /tmp/job489_gridcmp.py t2 1 2>&1 | grep -aE '^====|LETHAL 셀'; measure t2
echo "## 3. 복귀: STVL·nvblox 정지"
QUICK=1 bash /tmp/job488_layer_ab.sh stvl $BX $BY 2>&1 | grep -aE '실행값|오류'; nv_stop
ls -la /tmp/grid_stvl3_*.json /tmp/grid_t4_*.json /tmp/grid_t2_*.json 2>/dev/null | awk '{print $5, $9}'
