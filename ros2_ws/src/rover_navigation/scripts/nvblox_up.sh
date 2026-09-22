#!/bin/bash
# nvblox 노드 기동 래퍼 (N6-0, 2026-09-22) — navigation.launch.py 의 ExecuteProcess 가 부른다.
#   1) Isaac ROS 컨테이너가 정지(재부팅 뒤 Exited)면 docker start, 없으면 실패(이미지 재생성은 사람이: Docs/debug_log/2026-09-21/jobs/job472_container.sh)
#   2) 컨테이너가 보는 /tmp 에 DDS 프로파일·nvblox 파라미터를 복사
#   3) 남아 있는 nvblox_node(실행 파일 경로 PID)를 정리한 뒤 컨테이너 안에서 nvblox_node 를 띄우고, 이 셸은 그 PID 를 지켜보며 산다
#   4) SIGTERM/SIGINT(launch 종료) 를 받으면 컨테이너 안 노드를 INT→KILL 로 정리하고 나간다 — docker exec 는 신호를 안 넘기므로 직접 죽인다
#   인자: <nvblox_params.yaml> [로그 경로=/tmp/nvblox_node.log]
#   깊이 리매핑은 Phase N0 부터 같음(camera_0/depth ← /camera/camera/depth/image_rect_raw). 통계 출력(print_*_to_console)이 로그로 가며 게이트 J 가 읽는다.
set -u
YAML=${1:?nvblox params yaml}; LOG=${2:-/tmp/nvblox_node.log}
CN=isaac_ros_dev-aarch64-container; BIN=/opt/ros/humble/lib/nvblox_ros/nvblox_node
DDS_SRC=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml
say() { echo "[nvblox_up] $*"; }
if ! docker ps --format '{{.Names}}' | grep -qx "$CN"; then
  if docker ps -a --format '{{.Names}}' | grep -qx "$CN"; then say "컨테이너 정지 상태 → docker start"; docker start "$CN" >/dev/null || { say "docker start 실패"; exit 2; }; sleep 4
  else say "컨테이너 $CN 없음 — job472_container.sh 로 재생성 필요"; exit 3; fi
fi
cp -f "$DDS_SRC" /tmp/fastdds_udp_only.xml 2>/dev/null || say "DDS 프로파일 복사 실패(계속)"
cp -f "$YAML" /tmp/nvblox_active.yaml || { say "yaml 복사 실패: $YAML"; exit 4; }
nv_pids() { docker exec "$CN" bash -c "pgrep -f '^$BIN' || true" 2>/dev/null; }
nv_kill() { local p; for p in $(nv_pids); do docker exec "$CN" kill -INT "$p" 2>/dev/null; done; sleep 2; for p in $(nv_pids); do docker exec "$CN" kill -9 "$p" 2>/dev/null; done; }
if [ -n "$(nv_pids)" ]; then say "이전 nvblox_node $(nv_pids | tr '\n' ' ')정리"; nv_kill; fi
cleanup() { nv_kill; say "종료 신호/부모 소멸 → 컨테이너 안 nvblox_node 정리 끝(남은 pid '$(nv_pids | tr '\n' ' ')')"; exit 0; }   # 죽이는 것을 먼저, 로그는 나중에
trap cleanup TERM INT HUP
docker exec -d -u admin --workdir /workspaces/isaac_ros-dev "$CN" bash -lc "export FASTRTPS_DEFAULT_PROFILES_FILE=/tmp/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; exec ros2 run nvblox_ros nvblox_node --ros-args --params-file /tmp/nvblox_active.yaml -r camera_0/depth/image:=/camera/camera/depth/image_rect_raw -r camera_0/depth/camera_info:=/camera/camera/depth/camera_info > $LOG 2>&1"
sleep 3; P=$(nv_pids | head -1)
[ -z "$P" ] && { say "nvblox_node 가 뜨지 않음 — $LOG 확인"; tail -5 "$LOG" 2>/dev/null; exit 5; }
say "nvblox_node pid $P (yaml $(basename "$YAML"), 로그 $LOG, 부모 launch pid $PPID) — 이후 래퍼 출력은 ${LOG%.log}_up.log"
# launch 가 먼저 죽으면 stdout 파이프가 끊겨 다음 echo 에서 SIGPIPE 로 래퍼가 정리도 못 하고 죽는다(09-22 N6-0 V2 2 차 진단) → 기동 뒤엔 파일로 쓰고 PIPE 는 무시
exec >> "${LOG%.log}_up.log" 2>&1; trap '' PIPE
# 감시 루프: (a) 노드가 스스로 죽으면 래퍼도 끝낸다(launch 로그에 남음) (b) 부모 launch 가 신호 없이 사라지면(PPID → 1) 스스로 정리한다.
#   setsid nohup 아래서 뜬 launch 는 자식에게 SIGINT 무시를 물려주므로 launch 의 1차 INT 는 이 셸에 닿지 않고(무시된 신호는 trap 불가), 5 s 뒤 TERM 만 닿는다 — 그래서 (b) 가 필요하다(09-22 N6-0 V2 진단).
while [ -n "$(nv_pids)" ]; do
  sleep 2
  if [ "$(ps -o ppid= -p $$ 2>/dev/null | tr -d ' ')" = "1" ]; then say "부모 launch 소멸 감지 → 정리"; cleanup; fi
done
say "nvblox_node 종료됨 — $LOG 꼬리:"; tail -5 "$LOG" 2>/dev/null; exit 6
