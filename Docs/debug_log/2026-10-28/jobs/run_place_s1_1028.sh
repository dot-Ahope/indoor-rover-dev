#!/bin/bash
# §7 F2.5 S1 실주행: 장소 이름 명령으로 no5 와 같은 순서 + W3 구간 정지 시험 + 돌아와. Jetson 에서 setsid nohup 으로 독립 실행(PC 끊겨도 계속, 10-28 §3.1).
#   출력 /tmp/place_s1.log · bag /tmp/bag_<NAME> · tegrastats /tmp/tegra_<NAME>.log · 서버 로그 /tmp/place_server_s1.log
set +u
NAME=${1:-f2pl1}; SRC=~/ros2_ws/src/rover_navigation
export FASTRTPS_DEFAULT_PROFILES_FILE=$HOME/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "########## S1 $NAME 게이트 $(date +%T) ##########"
GT=$(timeout 40 python3 /tmp/chk_drive_gate.py 2>&1 | grep -av "^\["); echo "$GT"; GL=$(echo "$GT" | grep -a "^GATE" | tail -1)
echo "$GL" | grep -q "B=OK" && echo "$GL" | grep -q "C=OK" || { echo "게이트 불합격 — 주행하지 않음"; exit 1; }
G2=$(echo "$GL" | grep -o "G2=[^ ]*" | cut -d= -f2); awk -v d="$G2" 'BEGIN{exit !(d+0>=0.10)}' || { echo "G2 불합격($G2) — 주행하지 않음"; exit 1; }
setsid nohup python3 $SRC/scripts/place_server.py --ros-args -p places_file:=$SRC/config/places.yaml > /tmp/place_server_s1.log 2>&1 &
PS=$!
BAG=/tmp/bag_$NAME; rm -rf $BAG
printf '/tf:\n  reliability: best_effort\n  history: keep_last\n  depth: 100\n  durability: volatile\n' > /tmp/bag_qos_$NAME.yaml
setsid nohup ros2 bag record -o $BAG --qos-profile-overrides-path /tmp/bag_qos_$NAME.yaml /tf /tf_static /map /scan /plan /plan_smoothed /local_costmap/costmap /global_costmap/costmap /odometry/filtered /wheel_odom /cmd_vel /battery /nvblox_node/static_map_slice /place/status /place/command > /tmp/bag_$NAME.log 2>&1 &
setsid nohup tegrastats --interval 1000 > /tmp/tegra_$NAME.log 2>&1 &
sleep 30   # DDS 참여자(서버 · 경로 조회기 · 기록기) 생성 뒤 30 s(09-21 규칙) — 그 사이 서버 준비
grep -a "장소\|조회기" /tmp/place_server_s1.log | tail -2
echo "########## S1 $NAME 명령 $(date +%T) ##########"
# §8: 둘째 인자 PLAN — full(기본, no5 순서 전체) · fromC(C 에서 다시 시작: B 구간을 뺀 나머지)
case "${2:-full}" in
  fromC) CMDS="where; go_to 통로 북쪽; go_to 남서; go_to 통로 북쪽; go_to 위 복도; go_to W3 @stop20; wait 5; go_to W3; return" ;;
  *)     CMDS="where; go_to B; go_to 위 복도; go_to 통로 북쪽; go_to 남서; go_to 통로 북쪽; go_to 위 복도; go_to W3 @stop20; wait 5; go_to W3; return" ;;
esac
echo "PLAN ${2:-full}: $CMDS"
python3 $SRC/scripts/place_cmd.py "$CMDS"
RC=$?; echo "########## S1 $NAME 끝 $(date +%T) rc $RC ##########"
pkill -INT -f "ros2 bag record -o $BAG" 2>/dev/null; pkill -f "tegrastats --interval 1000" 2>/dev/null
kill -INT $PS 2>/dev/null; sleep 3; kill -9 $PS 2>/dev/null; pkill -f "path_end_yaw.py --serve" 2>/dev/null
for i in $(seq 1 10); do [ "$(pgrep -fc "ros2 bag record -o $BAG")" = 0 ] && break; sleep 1; done
tar czf /tmp/bag_$NAME.tgz -C /tmp bag_$NAME 2>/dev/null; echo "=== 끝 $(date +%T) bag $(stat -c %s /tmp/bag_$NAME.tgz 2>/dev/null) B ==="
