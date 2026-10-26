#!/bin/bash
# run_planner_offline — (Jetson) ROS_DOMAIN_ID 42 에 오프라인 planner_server + 수명 관리자 + map→base_link 고정 TF 를 띄우고 query_planners.py 실행 뒤 모두 정리 (2026-10-23, 로버 안 움직임).
#   입력: /tmp/planoff/{planner_offline.yaml, query_planners.py, scenes.npz}. 출력: /tmp/planoff/result.npz 와 로그. 주행 스택(기본 도메인)과 섞이지 않게 도메인 42.
#   인자: planner_id 목록(쉼표)
D=/tmp/planoff; cd $D; export ROS_DOMAIN_ID=42
source /opt/ros/humble/setup.bash
PIDS=${1:-GridBased}
# 2026-10-26 §5: 두 번째 인자 = 오버레이 작업공간(예 ~/smac_ws — Smac 포크). 주면 /opt/ros 위에 덧씌움
OV=${2:-}; if [ -n "$OV" ]; then source $OV/install/setup.bash; echo "오버레이 $OV · nav2_smac_planner = $(ros2 pkg prefix nav2_smac_planner)"; fi
# 2026-10-26: 앞 실행의 잔재가 있으면 액션 서버가 여럿이 되어 결과가 섞임(D5 첫 판 무효) — 시작 전에 확인하고 있으면 중단
n0=$(pgrep -fc '/tmp/planoff/planner_offline'); if [ "$n0" != 0 ]; then echo "중단: 앞 실행 잔재 $n0 개 — kill_planoff 로 정리 뒤 다시"; exit 1; fi
setsid ros2 run nav2_planner planner_server --ros-args --params-file $D/planner_offline.yaml > $D/planner.log 2>&1 &
setsid ros2 run nav2_lifecycle_manager lifecycle_manager --ros-args -r __node:=lifecycle_manager_offline --params-file $D/planner_offline.yaml > $D/lcm.log 2>&1 &
setsid ros2 run tf2_ros static_transform_publisher --frame-id map --child-frame-id base_link > $D/tf.log 2>&1 &
sleep 6
python3 -u $D/query_planners.py $D/scenes.npz $D/result.npz "$PIDS" 2>&1 | tee $D/query.log
# 2026-10-26 §5.2: 어떤 Smac 이 실제로 실렸나 — 질의가 끝난 뒤(기동 완료 후) 매개변수 · 적재된 .so 경로로 확인
P1=$(echo "$PIDS" | tr ',' '
' | grep -v GridBased | head -1)
[ -n "$P1" ] && echo "확인: $P1.analytic_expansion_max_cost = $(timeout 10 ros2 param get /planner_server $P1.analytic_expansion_max_cost 2>&1 | tail -1)"
PS=$(pgrep -f 'lib/nav2_planner/planner_server --ros-args --params-file /tmp/planoff' | head -1); [ -n "$PS" ] && echo "적재된 smac .so: $(grep -o '/[^ ]*libnav2_smac_planner\.so' /proc/$PS/maps 2>/dev/null | sort -u | tr '
' ' ')"
# 정리: 이 스크립트가 띄운 세 프로세스 묶음만(setsid 로 각자 프로세스 그룹)
for p in $(pgrep -f "planner_offline.yaml|static_transform_publisher --frame-id map --child-frame-id base_link"); do kill -INT -$(ps -o pgid= $p | tr -d ' ') 2>/dev/null; done
sleep 2; echo "남은 오프라인 프로세스: $(pgrep -fc 'planner_offline.yaml')"
grep -aiE "error|exception|warn" $D/planner.log | grep -v "tick rate" | sort | uniq -c | sort -rn | head -12
echo "RESULT_B64_BEGIN"; base64 -w0 $D/result.npz; echo; echo "RESULT_B64_END"
