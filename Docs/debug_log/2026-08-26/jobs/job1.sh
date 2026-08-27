#!/bin/bash
# Step 1: micro-ros-agent 컨테이너 실행 (심볼릭 링크 resolve 후 전달)
REAL_DEV=$(readlink -f /dev/rover)
echo "REAL_DEV=$REAL_DEV"
docker rm -f microros_agent >/dev/null 2>&1
docker run -d --name microros_agent --net host \
  --device "$REAL_DEV:/dev/rover" \
  microros/micro-ros-agent:humble serial --dev /dev/rover -b 2000000 -v4
sleep 8
echo "===AGENT_LOGS==="
docker logs microros_agent 2>&1 | tail -15
