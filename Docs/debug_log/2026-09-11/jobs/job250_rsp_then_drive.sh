#!/bin/bash
# robot_state_publisher 중복 판정 → 프로세스가 정확히 1개일 때만 주행.
set +u
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "=== robot_state_publisher ==="
echo "  프로세스: $(pgrep -fc robot_state_publisher | head -1)개"
pgrep -fa robot_state_publisher | sed 's/^/    /' | cut -c1-110
echo "  base.launch 프로세스: $(pgrep -fc 'base.launch' | head -1)개"
echo "  그래프 상 이름 중복: $(ros2 node list 2>/dev/null | grep -c '^/robot_state_publisher$')회"
echo "  /tf_static 발행자 GID 별:"
timeout 8 ros2 topic info /tf_static --verbose 2>/dev/null | grep -aE "Node name|GID" | paste - - | grep -a robot_state | sed 's/^/    /' | cut -c1-120
RSP=$(pgrep -fc robot_state_publisher | head -1); RSP=${RSP:-0}
if [ "$RSP" != "1" ]; then
  echo "  ★ robot_state_publisher 프로세스 $RSP개 — 주행 중단. 정리 필요."
  exit 1
fi
echo "  → 프로세스 1개. 그래프 중복은 DDS 잔상(UDP 참가자 lease 만료 대기)으로 판단, 주행 진행."
echo
bash /tmp/job231_drive.sh job251 1.60 90
