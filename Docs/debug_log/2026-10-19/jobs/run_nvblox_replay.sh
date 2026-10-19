#!/bin/bash
# (10-19 §2) 기록한 깊이 bag 을 컨테이너 nvblox 에 다시 넣어 거리 지도 조각을 얻는다 — 설정만 바꾼 오프라인 A/B 용. 로버 안 움직임
#   인자: <깊이 bag 경로> <꼬리표> [nvblox 파라미터 덮어쓰기 'name:=value' ...]
#   격리: 재생 nvblox · bag play · 출력 기록은 모두 ROS_DOMAIN_ID=42 (실시간 스택은 0) — 같은 토픽 이름이어도 섞이지 않음
#   시간: bag play --clock + nvblox use_sim_time:=true (bag 의 tf · 깊이 시각 그대로)
#   기본 파라미터 = 실시간과 같은 nvblox_local.yaml(설치본). 출력 = ~/bags/replay_<꼬리표>(/nvblox_node/static_map_slice), 로그 /tmp/nvblox_replay_<꼬리표>.log
set -u
IN=${1:?bag}; TAG=${2:?tag}; shift 2
CN=isaac_ros_dev-aarch64-container
Y=/home/jetson/ros2_ws/install/rover_navigation/share/rover_navigation/config/nvblox_local.yaml
OUT=/home/jetson/bags/replay_$TAG; rm -rf "$OUT"; LOG=/tmp/nvblox_replay_$TAG.log
docker ps --format '{{.Names}}' | grep -qx "$CN" || { echo "컨테이너 $CN 꺼져 있음"; exit 2; }
cp -f "$Y" /tmp/nvblox_replay.yaml
cp -f /home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml /tmp/fastdds_udp_only.xml
PO="-p use_sim_time:=true"; for a in "$@"; do PO="$PO -p $a"; done
echo "재생 nvblox 덮어쓰기: $PO"
docker exec -d -u admin --workdir /workspaces/isaac_ros-dev "$CN" bash -lc "export ROS_DOMAIN_ID=42 FASTRTPS_DEFAULT_PROFILES_FILE=/tmp/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; exec ros2 run nvblox_ros nvblox_node --ros-args --params-file /tmp/nvblox_replay.yaml $PO -r camera_0/depth/image:=/camera/camera/depth/image_rect_raw -r camera_0/depth/camera_info:=/camera/camera/depth/camera_info > $LOG 2>&1"
sleep 6
RP=$(docker exec "$CN" bash -c "pgrep -f 'nvblox_replay.yaml' | head -1")
[ -z "$RP" ] && { echo "재생 nvblox 가 뜨지 않음"; tail -5 $LOG; exit 3; }
export ROS_DOMAIN_ID=42
ros2 bag record -o "$OUT" /nvblox_node/static_map_slice > /tmp/replay_rec_$TAG.log 2>&1 &
RECP=$!; sleep 3
T0=$(date +%s); # 10-19 §6: 입력 토픽만 재생 — 주행 bag 에 든 실시간 조각까지 내보내면 출력 기록에 섞인다(첫 R0 에서 조각 수 2 배)
ros2 bag play "$IN" --clock 100 --topics /camera/camera/depth/image_rect_raw /camera/camera/depth/camera_info /tf /tf_static > /tmp/replay_play_$TAG.log 2>&1; echo "재생 끝 $(( $(date +%s) - T0 )) s"
sleep 3; kill -INT $RECP; sleep 3
# 10-19 §15 정정: $RP 는 ros2 run 래퍼라 그것만 죽이면 nvblox_node 가 고아로 남았다(4 개 발견) → 패턴으로 모두
docker exec "$CN" bash -c "pkill -INT -f nvblox_replay.yaml; sleep 2; pkill -9 -f nvblox_replay.yaml" 2>/dev/null
echo "재생 nvblox 로그 꼬리:"; grep -a "integrat\|depth\|ERROR\|WARN" $LOG | tail -4 | cut -c1-200
ros2 bag info "$OUT" 2>/dev/null | grep -E "Bag size|Duration|Count" | sed 's/Serialization Format: cdr//'
echo "출력 $OUT"
