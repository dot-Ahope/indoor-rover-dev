#!/bin/bash
# Step 2: 워크스페이스 구성 → colcon 빌드 → base.launch.py 기동 → 검증
set -e
source /opt/ros/humble/setup.bash

mkdir -p ~/ros2_ws/src
cp -r /tmp/rover_src/rover_description /tmp/rover_src/rover_bringup ~/ros2_ws/src/

cd ~/ros2_ws
echo "===COLCON_BUILD==="
colcon build --symlink-install 2>&1 | tail -8

# 기존 단독 agent 컨테이너 정지 (launch가 같은 이름으로 다시 띄움)
docker rm -f microros_agent >/dev/null 2>&1 || true

source ~/ros2_ws/install/setup.bash
echo "===LAUNCH_START==="
setsid nohup ros2 launch rover_bringup base.launch.py > /tmp/bringup.log 2>&1 &
echo $! > /tmp/bringup.pid
sleep 18

echo "===BRINGUP_LOG_TAIL==="
tail -6 /tmp/bringup.log
echo "===DOCKER_PS==="
docker ps --format '{{.Names}} {{.Status}}' | grep microros_agent || echo AGENT_CONTAINER_DOWN
echo "===NODE_LIST==="
ros2 node list
echo "===HZ_WHEEL_ODOM==="
timeout 8 ros2 topic hz /wheel_odom 2>&1 | tail -2 || true
echo "===RSP_PARAM==="
ros2 param get /robot_state_publisher robot_description 2>/dev/null | head -c 120; echo
echo "===TF_STATIC==="
timeout 8 ros2 topic echo /tf_static --qos-durability transient_local --qos-reliability reliable 2>/dev/null | grep -E "frame_id|child_frame_id" | head -12 || echo TF_STATIC_NOT_SEEN
