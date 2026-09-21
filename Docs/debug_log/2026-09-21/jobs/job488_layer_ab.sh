#!/bin/bash
# N3 정지 A/B (2026-09-21): 로컬 코스트맵 카메라 층을 stvl|nvblox 로 바꿔 Nav2 만 재기동 → 로컬 코스트맵의 상자 셀·근거 없는 셀·창·CPU 를 같은 자세에서 비교. 인자: stvl|nvblox [BX BY]
#   설치본 YAML 의 plugins 두 줄(활성/주석)을 맞바꾼다(재빌드 없음). 주행 없음. 끝나면 이 스크립트로 stvl 로 되돌린다.
set +u
MODE=$1; BX=${2:-1.15}; BY=${3:-0.10}
export FASTRTPS_DEFAULT_PROFILES_FILE=$HOME/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
Y=~/ros2_ws/install/rover_navigation/share/rover_navigation/config/nav2_params.yaml
if [ "$MODE" = nvblox ]; then
  sed -i -e 's/^      plugins: \["stvl_layer", "obstacle_layer", "inflation_layer"\]/      # plugins: ["stvl_layer", "obstacle_layer", "inflation_layer"]/' -e 's/^      # plugins: \["nvblox_layer", "obstacle_layer", "inflation_layer"\]/      plugins: ["nvblox_layer", "obstacle_layer", "inflation_layer"]/' $Y
else
  sed -i -e 's/^      # plugins: \["stvl_layer", "obstacle_layer", "inflation_layer"\]/      plugins: ["stvl_layer", "obstacle_layer", "inflation_layer"]/' -e 's/^      plugins: \["nvblox_layer", "obstacle_layer", "inflation_layer"\]/      # plugins: ["nvblox_layer", "obstacle_layer", "inflation_layer"]/' $Y
fi
echo "== 활성 plugins(로컬): $(grep -nE '^      plugins:' $Y | head -1 | cut -c1-90)"
echo "== Nav2 재기동"
for p in navigation.launch navigation_launch controller_server planner_server bt_navigator behavior_server velocity_smoother smoother_server waypoint_follower lifecycle_manager stuck_monitor; do pkill -TERM -f "$p" 2>/dev/null; done; sleep 6
for p in controller_server planner_server bt_navigator behavior_server velocity_smoother smoother_server lifecycle_manager; do pkill -9 -f "$p" 2>/dev/null; done; sleep 2
: > /tmp/nav2.log; setsid nohup ros2 launch rover_navigation navigation.launch.py stuck_shadow:=true > /tmp/nav2.log 2>&1 &
sleep 35
echo "  nav2 프로세스: controller $(pgrep -fc controller_server) planner $(pgrep -fc planner_server) bt $(pgrep -fc bt_navigator) | 오류: $(grep -aciE 'error|failed to load|exception' /tmp/nav2.log)"
grep -aiE "nvblox|Failed to load|plugin|error" /tmp/nav2.log | grep -aiv "Using plugin\|debug" | head -6 | cut -c1-170
echo "  로컬 plugins 실행값: $(timeout 12 ros2 param get /local_costmap/local_costmap plugins 2>&1 | tail -1 | cut -c1-100)"
timeout 10 ros2 service call /local_costmap/clear_entirely_local_costmap nav2_msgs/srv/ClearEntireCostmap "{}" >/dev/null 2>&1; sleep 10
echo "== 로컬 코스트맵 상자 셀·띠·창 (job248 감사, 3 표본)"; for i in 1 2 3; do BOX_HINT="$BX $BY" timeout 100 python3 /tmp/job248_audit.py 2>&1 | grep -aE "^상자|로컬\[|최소폭|상자 셀" | head -4 | cut -c1-170; sleep 2; done
echo "== 로컬 LETHAL 셀 vs 라이다/카메라 근거 (job315)"; timeout 60 python3 /tmp/job315_boxcells.py 2>&1 | grep -av '^\[' | head -6 | cut -c1-170
echo "== CPU 20 s(top 2 회 평균): $(top -b -n2 -d10 2>/dev/null | awk '/PID +USER/{f++} f==2' | awk '$12 ~ /controller|planner|depth_relay|nvblox|python3/ {printf "%s %s%% | ", $12, $9}') load $(cut -d' ' -f1-3 /proc/loadavg)"
echo "== 로컬 코스트맵 발행: $(timeout 8 ros2 topic hz /local_costmap/costmap 2>&1 | grep -ao 'average rate: [0-9.]*' | head -1)"
