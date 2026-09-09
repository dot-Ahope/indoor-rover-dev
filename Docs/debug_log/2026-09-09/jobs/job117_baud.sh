#!/bin/bash
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
cp /tmp/base.launch.py ~/ros2_ws/src/rover_bringup/launch/base.launch.py
cp /tmp/base.launch.py ~/ros2_ws/install/rover_bringup/share/rover_bringup/launch/base.launch.py
echo "배포 확인: $(grep -aoE "'-b', '[0-9]+'" ~/ros2_ws/install/rover_bringup/share/rover_bringup/launch/base.launch.py)"
docker rm -f microros_agent >/dev/null 2>&1
for p in "base.launch" "robot_state_publisher"; do pkill -9 -f "$p" 2>/dev/null; done
sleep 3
setsid nohup ros2 launch rover_bringup base.launch.py > /tmp/base.log 2>&1 &
sleep 12
docker inspect -f '  agent Cmd: {{join .Config.Cmd " "}}' microros_agent 2>/dev/null || echo "  agent 없음"
