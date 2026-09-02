#!/bin/bash
# 스택 재시작: base(agent+RSP) + sensors(camera+lidar+ekf+foxglove). agent 재시작 → 보드 RESET 필요.
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "===현재 상태==="; uptime | cut -c1-40; echo "nodes: $(ros2 node list 2>/dev/null | tr '\n' ' ')"
echo "===agent 확인==="; docker ps --format '{{.Names}} {{.Status}}' | grep microros || echo NO_AGENT
echo "===stale 정리==="
for p in "base.launch" "sensors.launch" "slam.launch" realsense2_camera_node rplidar_node scan_deskew ekf_node sensor_conditioner foxglove_bridge robot_state_publisher slam_toolbox teleop joy_linux; do pkill -f "$p" 2>/dev/null; done
docker rm -f microros_agent >/dev/null 2>&1; sleep 3
echo "===base.launch 기동==="
setsid nohup ros2 launch rover_bringup base.launch.py > /tmp/bringup.log 2>&1 &
sleep 10
docker ps --format '{{.Names}} {{.Status}}' | grep microros_agent || echo AGENT_DOWN
echo "===sensors.launch 기동==="
setsid nohup ros2 launch rover_bringup sensors.launch.py > /tmp/sensors.log 2>&1 &
sleep 30
echo "노드: $(ros2 node list | grep -E 'rover_jupiter|ekf|scan_deskew|camera|rplidar' | tr '\n' ' ')"
echo -n "  wheel_odom(RESET 전엔 무발행): "; timeout 5 ros2 topic hz /wheel_odom 2>&1 | grep -aE "average|does not" | tail -1
echo "NEXT: 보드 RESET 버튼 → 세션 재수립"
