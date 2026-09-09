#!/bin/bash
# agent 를 -v6(DEBUG) 로 띄워 보드가 실제로 어떤 datawriter 로 몇 개를 보내는지 센다.
# base.launch 가 관리하던 컨테이너를 내리므로 robot_state_publisher 를 따로 살린다.
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash

echo "=== 기존 agent 내리기 ==="
docker rm -f microros_agent >/dev/null 2>&1
for p in "base.launch"; do pkill -9 -f "$p" 2>/dev/null; done
sleep 3
ROVER_DEV=$(readlink -f /dev/rover)
echo "  실장치: $ROVER_DEV"

echo "=== robot_state_publisher 재기동 ==="
setsid nohup ros2 launch rover_description description.launch.py > /tmp/rsp.log 2>&1 &
sleep 4
echo "  RSP: $(ros2 node list 2>/dev/null | grep -a robot_state_publisher || echo 없음)"

echo "=== agent -v6 기동 (로그 /tmp/agent_v6.log) ==="
setsid nohup docker run --rm --name microros_agent --net host \
  --device ${ROVER_DEV}:/dev/rover microros/micro-ros-agent:humble \
  serial --dev /dev/rover -b 2000000 -v6 > /tmp/agent_v6.log 2>&1 &
sleep 8
docker ps --format '{{.Names}} {{.Status}}' | grep -a microros | sed 's/^/  /'
echo ""
echo ">>> 보드 RESET 버튼을 눌러 주세요. 60초 뒤 자동 집계합니다. <<<"
