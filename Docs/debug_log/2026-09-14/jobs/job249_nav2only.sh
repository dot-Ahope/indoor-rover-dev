#!/bin/bash
# nav2 만 재기동 — 중복 프로세스 없이. base/sensors/slam 은 건드리지 않는다(보드 세션 유지).
set +u
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
tr -d '\r' < /tmp/nav2_params.yaml > /tmp/np.u && mv /tmp/np.u /tmp/nav2_params.yaml
python3 - <<'PY' || { echo "YAML 검증 실패 — 중단"; exit 1; }
import yaml
d=yaml.safe_load(open('/tmp/nav2_params.yaml'))
v=d['controller_server']['ros__parameters']['FollowPath']['max_allowed_time_to_collision_up_to_carrot']
assert v==1.5, v
for cm in ('local_costmap','global_costmap'):
    cp=d[cm][cm]['ros__parameters']
    for pl in cp['plugins']: assert 'plugin' in cp[pl], (cm,pl)
print("  YAML OK: collision horizon =", v)
PY
cp /tmp/nav2_params.yaml ~/ros2_ws/src/rover_navigation/config/
cp /tmp/nav2_params.yaml ~/ros2_ws/install/rover_navigation/share/rover_navigation/config/

cnt1() { local c; c=$(pgrep -fc "$1" 2>/dev/null | head -1); echo "${c:-0}"; }
NAV="navigation.launch controller_server planner_server bt_navigator behavior_server velocity_smoother smoother_server waypoint_follower lifecycle_manager stuck_monitor"
KEEP="base.launch microros_agent robot_state_publisher sensors.launch realsense2_camera rplidar sensor_conditioner ekf_node scan_deskew slam.launch slam_toolbox"

echo "=== 재기동 전 프로세스 수 ==="
for p in $KEEP; do printf "  %-22s %s\n" "$p" "$(cnt1 $p)"; done | sed 's/^/ 유지 /'
for p in $NAV;  do printf "  %-22s %s\n" "$p" "$(cnt1 $p)"; done | sed 's/^/ nav2 /'

echo "=== nav2 SIGTERM ==="
for p in $NAV; do pkill -TERM -f "$p" 2>/dev/null; done
for i in $(seq 1 15); do
  n=0; for p in $NAV; do n=$((n+$(cnt1 $p))); done
  [ "$n" = "0" ] && break; sleep 1
done
n=0; for p in $NAV; do n=$((n+$(cnt1 $p))); done
if [ "$n" != "0" ]; then
  echo "  잔존 $n → SIGKILL"; for p in $NAV; do pkill -9 -f "$p" 2>/dev/null; done; sleep 3
fi
n=0; for p in $NAV; do n=$((n+$(cnt1 $p))); done
echo "  nav2 잔존: $n"
echo "  유지 계층 손상 여부:"
BAD=0
for p in realsense2_camera rplidar sensor_conditioner ekf_node slam_toolbox; do
  c=$(cnt1 $p); [ "$c" != "1" ] && BAD=1
  printf "    %-20s %s\n" "$p" "$c"
done
[ "$BAD" = "1" ] && { echo "  ★ 유지 계층이 1개가 아니다 — 중단. 전체 재기동(job240_clean) 필요"; exit 1; }
[ "$(docker ps --format '{{.Names}}' | grep -c microros_agent)" = "1" ] || { echo "  ★ 에이전트 컨테이너 없음 — 중단"; exit 1; }

echo "=== nav2 기동 ==="
: > /tmp/nav2.log
setsid nohup ros2 launch rover_navigation navigation.launch.py > /tmp/nav2.log 2>&1 &
sleep 30
for nd in /controller_server /planner_server /bt_navigator /behavior_server; do
  printf "  %-20s " "$nd"; timeout 6 ros2 lifecycle get "$nd" 2>/dev/null || echo "?"
done
echo "  적용값: $(timeout 8 ros2 param get /controller_server FollowPath.max_allowed_time_to_collision_up_to_carrot 2>/dev/null | sed 's/^.*is: //')"
echo "  BT 로드 오류: $(grep -aci 'not registered\|Failed to load' /tmp/nav2.log)건"

echo "=== 중복 감사 (전 스택, 각 1이어야) ==="
DUP=0
for p in microros_agent robot_state_publisher realsense2_camera rplidar sensor_conditioner ekf_node scan_deskew slam_toolbox controller_server planner_server bt_navigator behavior_server lifecycle_manager stuck_monitor; do
  c=$(cnt1 $p); [ "$c" != "1" ] && DUP=1
  printf "  %-20s %s%s\n" "$p" "$c" "$([ "$c" != "1" ] && echo '  ← !!')"
done
echo "  ros2 노드 중복: $(ros2 node list 2>/dev/null | sort | uniq -d | tr '\n' ' ')"
echo "  /tf 발행자: $(timeout 8 ros2 topic info /tf --verbose 2>/dev/null | grep -a 'Node name' | sed 's/.*: //' | sort | uniq -c | awk '{printf "%s x%s  ", $2, $1}')"
[ "$DUP" = "1" ] && { echo "  ★ 중복/누락 있음 — 주행 금지"; exit 1; }
echo "  load: $(cut -d' ' -f1-3 /proc/loadavg)"

echo "=== 코스트맵 클리어 + 15초 ==="
timeout 10 ros2 service call /local_costmap/clear_entirely_local_costmap nav2_msgs/srv/ClearEntireCostmap "{}" >/dev/null 2>&1
timeout 10 ros2 service call /global_costmap/clear_entirely_global_costmap nav2_msgs/srv/ClearEntireCostmap "{}" >/dev/null 2>&1
sleep 15
echo -n "  로버 자세: "; timeout 6 ros2 run tf2_ros tf2_echo map base_link 2>&1 | grep -aE "Translation|RPY" | head -2 | tr '\n' ' '; echo
echo "=== 통과 가능성 (job248) ==="
python3 /tmp/job248_audit.py 2>&1 | sed -n '6,12p;36,40p'
