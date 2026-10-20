#!/bin/bash
# cuVSLAM 기동 래퍼 (2026-10-20 §6) — ekf.launch.py vslam:=shadow|on 이 ExecuteProcess 로 부른다. nvblox_up.sh 와 같은 방식:
#   1) Isaac ROS 컨테이너가 정지면 docker start  2) 컨테이너가 보는 /tmp 에 DDS 프로파일 · launch 복사
#   3) 남은 cuVSLAM 정리 → 컨테이너 안에서 ros2 launch, 이 셸은 그것을 지켜보며 산다
#   4) SIGTERM/SIGINT 또는 부모 launch 소멸(PPID 1) 이면 컨테이너 안 프로세스를 INT → KILL 로 정리
#   인자: <cuvslam_container.launch.py> [로그=/tmp/cuvslam.log] [DDS 프로파일=UDP 전용] — 10-20 §7.4: SHM 이면 fastdds_shm_udp.xml
set -u
LP=${1:?launch path}; LOG=${2:-/tmp/cuvslam.log}
CN=isaac_ros_dev-aarch64-container; PAT='cuvslam_[a]ctive.launch.py|__node:=cuvslam_[c]ontainer'   # [ ] = pgrep 이 자기를 부른 bash -c 줄을 잡지 않게
DDS_SRC=${3:-/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml}
say() { echo "[cuvslam_up] $*"; }
if ! docker ps --format '{{.Names}}' | grep -qx "$CN"; then
  if docker ps -a --format '{{.Names}}' | grep -qx "$CN"; then say "컨테이너 정지 상태 → docker start"; docker start "$CN" >/dev/null || { say "docker start 실패"; exit 2; }; sleep 4
  else say "컨테이너 $CN 없음"; exit 3; fi
fi
cp -f "$DDS_SRC" /tmp/fastdds_cuvslam.xml 2>/dev/null || say "DDS 프로파일 복사 실패(계속)"   # 10-20: nvblox 가 쓰는 /tmp/fastdds_udp_only.xml 과 이름 분리
cp -f "$LP" /tmp/cuvslam_active.launch.py || { say "launch 복사 실패: $LP"; exit 4; }
cv_pids() { docker exec "$CN" bash -c "pgrep -f '$PAT' || true" 2>/dev/null; }
cv_kill() { local p; for p in $(cv_pids); do docker exec "$CN" kill -INT "$p" 2>/dev/null; done; sleep 3; for p in $(cv_pids); do docker exec "$CN" kill -9 "$p" 2>/dev/null; done; }
[ -n "$(cv_pids)" ] && { say "이전 cuVSLAM $(cv_pids | tr '\n' ' ')정리"; cv_kill; }
cleanup() { cv_kill; say "정리 끝(남은 '$(cv_pids | tr '\n' ' ')')"; exit 0; }
trap cleanup TERM INT HUP
docker exec -d -u admin --workdir /workspaces/isaac_ros-dev "$CN" bash -lc "export FASTRTPS_DEFAULT_PROFILES_FILE=/tmp/fastdds_cuvslam.xml; source /opt/ros/humble/setup.bash; exec ros2 launch /tmp/cuvslam_active.launch.py > $LOG 2>&1"
sleep 4; [ -z "$(cv_pids)" ] && { say "cuVSLAM 이 뜨지 않음 — $LOG"; tail -5 "$LOG" 2>/dev/null; exit 5; }
say "cuVSLAM pid $(cv_pids | tr '\n' ' ')(로그 $LOG, DDS $(basename "$DDS_SRC"), 부모 launch $PPID) — 이후 래퍼 출력은 ${LOG%.log}_up.log"
exec >> "${LOG%.log}_up.log" 2>&1; trap '' PIPE   # nvblox_up.sh 09-22 진단과 같은 이유
while [ -n "$(cv_pids)" ]; do
  sleep 2
  if [ "$(ps -o ppid= -p $$ 2>/dev/null | tr -d ' ')" = "1" ]; then say "부모 launch 소멸 감지 → 정리"; cleanup; fi
done
say "cuVSLAM 종료됨 — $LOG 꼬리:"; tail -5 "$LOG" 2>/dev/null; exit 6
