#!/bin/bash
# 재부팅 후 전체 스택 재시작: base(agent+RSP) + sensors(lidar+scan_restamp+camera+ekf+foxglove) + slam
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "===stale 정리==="
for p in "base.launch" "sensors.launch" "slam.launch" "lidar.launch" "ekf.launch" realsense2_camera_node rplidar_node scan_restamp ekf_node sensor_conditioner foxglove_bridge robot_state_publisher slam_toolbox; do pkill -f "$p" 2>/dev/null; done
docker rm -f microros_agent >/dev/null 2>&1; sleep 3
echo "===base.launch (agent+RSP)==="
setsid nohup ros2 launch rover_bringup base.launch.py > /tmp/bringup.log 2>&1 &
sleep 10
docker ps --format '{{.Names}} {{.Status}}' | grep microros_agent || echo AGENT_DOWN
echo "===sensors.launch (lidar+scan_restamp+camera+ekf+foxglove)==="
setsid nohup ros2 launch rover_bringup sensors.launch.py > /tmp/sensors.log 2>&1 &
sleep 30
echo "===slam.launch==="
setsid nohup ros2 launch rover_bringup slam.launch.py > /tmp/slam.log 2>&1 &
sleep 12
echo "===노드 목록==="; ros2 node list | tr '\n' ' '; echo
echo "===scan_restamp 확인==="; ros2 node list | grep -q scan_restamp && echo "scan_restamp OK" || echo "scan_restamp 없음"
echo -n "  /scan hz: "; timeout 5 ros2 topic hz /scan 2>&1 | grep -aoE "average rate: [0-9.]+" | tail -1
echo "===보드 세션 (RESET 전엔 무발행)==="
echo -n "  wheel_odom: "; timeout 5 ros2 topic hz /wheel_odom 2>&1 | grep -aE "average|does not" | tail -1
echo "NEXT: 보드 RESET 버튼 → 세션 재수립"
