#!/bin/bash
# -v6 진단 에이전트를 정상 에이전트로 되돌린다 (base.launch 경유).
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "=== -v6 로그 크기 ==="
ls -lh /tmp/agent_v6.log 2>/dev/null | awk '{print "  " $5 "  " $9}'
echo "=== 정리 ==="
docker rm -f microros_agent >/dev/null 2>&1
for p in "base.launch" "robot_state_publisher" "description.launch"; do pkill -9 -f "$p" 2>/dev/null; done
rm -f /tmp/agent_v6.log
sleep 3
echo "=== base.launch (정상 agent + RSP) ==="
setsid nohup ros2 launch rover_bringup base.launch.py > /tmp/base.log 2>&1 &
sleep 12
docker ps --format '{{.Names}} {{.Status}}' | grep -a microros | sed 's/^/  /' || echo "  AGENT 없음"
docker inspect -f '  Cmd: {{join .Config.Cmd " "}}' microros_agent 2>/dev/null
echo "  RSP: $(ros2 node list 2>/dev/null | grep -a robot_state_publisher || echo 없음)"
echo ""
echo ">>> 이제 보드 리셋 필요 <<<"
