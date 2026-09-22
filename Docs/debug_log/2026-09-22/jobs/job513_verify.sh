#!/bin/bash
# N6-0 검증(Jetson 측, 2026-09-22): rover_navigation 재빌드 → V1 nvblox 기본 기동·게이트 J·K·L → V2 launch 종료 시 노드 정리 → V3 camera_layer:=stvl → V4 컨테이너 정지 상태 복구. (V5 prep 재기동은 PC 의 run_mp9prep 로)
set +u
export TERM=xterm FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash
CN=isaac_ros_dev-aarch64-container; BIN=/opt/ros/humble/lib/nvblox_ros/nvblox_node
nvc() { docker exec $CN bash -c "pgrep -fc '^$BIN' || true" 2>/dev/null; }
nvp() { docker exec $CN bash -c "pgrep -f '^$BIN' || true" 2>/dev/null | head -1; }
echo "## 0. 빌드"; cd ~/ros2_ws; T0=$(date +%s); colcon build --symlink-install --packages-select rover_navigation 2>&1 | grep -aE "Finished|Failed|error" | tail -3; echo "  $(( $(date +%s) - T0 )) s | 설치: $(ls ~/ros2_ws/install/rover_navigation/share/rover_navigation/scripts/ 2>/dev/null | tr '\n' ' ') $(ls ~/ros2_ws/install/rover_navigation/share/rover_navigation/launch/ | tr '\n' ' ')"
source ~/ros2_ws/install/setup.bash; python3 -c "import yaml; print('  pyyaml OK')"
echo "## V1. camera_layer 기본(nvblox) — Nav2 재기동"
QUICK=1 bash /tmp/job488_layer_ab.sh nvblox 1.153 -0.089 2>&1 | grep -aE '실행값|오류'
echo "  nav2.log 의 nvblox_up: $(grep -a 'nvblox_up' /tmp/nav2.log | tail -2 | cut -c1-120 | tr '\n' '|')"
sleep 8; bash /tmp/job505_modeN_gate.sh node 1.153 -0.089 2>&1 | grep -aE '^[JKL] |==' | cut -c1-140
echo "  활성 yaml 머리: $(head -1 /tmp/nav2_params_active.yaml | cut -c1-90) | plugins 줄: $(grep -a -A1 'local_costmap:' /tmp/nav2_params_active.yaml | head -0; python3 -c "import yaml; print(yaml.safe_load(open('/tmp/nav2_params_active.yaml'))['local_costmap']['local_costmap']['ros__parameters']['plugins'])")"
echo "## V2. launch 종료 → 컨테이너 안 노드 정리"
P=$(nvp); W=$(pgrep -f "bash .*nvblox_up.sh" | head -1); T0=$(date +%s); pkill -TERM -f "navigation.launch" 2>/dev/null
for i in $(seq 1 25); do [ "$(nvc)" = "0" ] && break; sleep 1; done
echo "  종료 전 node $P/래퍼 $W → $(( $(date +%s) - T0 )) s 뒤 nvblox_node $(nvc) 개, 래퍼 생존 $(kill -0 $W 2>/dev/null && echo yes || echo no) | 래퍼 로그: $(tail -3 /tmp/nvblox_node_up.log 2>/dev/null | sed 's/.*\[nvblox_up\] //' | cut -c1-70 | tr '\n' '|')"
# 래퍼는 -9 로 죽이지 않는다(정리 기회를 없앰). 나머지 Nav2 잔존만 정리, 노드가 남았으면 다음 시나리오를 위해 직접 정리
for p in navigation_launch controller_server planner_server bt_navigator behavior_server velocity_smoother smoother_server waypoint_follower lifecycle_manager stuck_monitor; do pkill -9 -f "$p" 2>/dev/null; done; sleep 2
[ "$(nvc)" != "0" ] && { echo "  (잔존 노드 직접 정리)"; for p in $(docker exec $CN bash -c "pgrep -f '^$BIN' || true"); do docker exec $CN kill -9 $p; done; pkill -TERM -f "bash .*nvblox_up.sh"; sleep 2; }
echo "## V3. camera_layer:=stvl"
QUICK=1 bash /tmp/job488_layer_ab.sh stvl 1.153 -0.089 2>&1 | grep -aE '실행값|오류'
echo "  nvblox_node $(nvc) 개 (0 이어야) | 활성 yaml: $(head -1 /tmp/nav2_params_active.yaml | cut -c1-80)"
echo "## V4. 컨테이너 정지(재부팅 모사) → nvblox 모드 재기동 → 래퍼 복구"
docker stop $CN >/dev/null 2>&1; echo "  docker stop → 상태 $(docker ps -a --filter name=$CN --format '{{.Status}}' | cut -c1-20)"
QUICK=1 bash /tmp/job488_layer_ab.sh nvblox 1.153 -0.089 2>&1 | grep -aE '실행값|오류'
echo "  컨테이너 $(docker ps --filter name=$CN --format '{{.Status}}' | cut -c1-20) | nvblox_node $(nvc) 개 | 래퍼 로그: $(grep -a 'nvblox_up' /tmp/nav2.log | tail -3 | cut -c1-90 | tr '\n' '|')"
sleep 30; echo "  30 s 뒤 깊이 콜백: $(grep -aA7 'NVBlox Rates' /tmp/nvblox_node.log | grep -aE 'ros/depth_image_callback' | awk '{print $NF}' | tail -1) Hz | plugins: $(timeout 12 ros2 param get /local_costmap/local_costmap plugins 2>&1 | tail -1 | cut -c1-70)"
echo "## 끝(모드 N 유지 — V5 는 PC 에서 run_mp9prep 로)"
