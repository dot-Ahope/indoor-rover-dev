#!/bin/bash
# 안전 종료: 모터 정지 → Jetson 노드/agent 종료. (펌웨어/보드 무관)
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "=== 모터 정지 (0 cmd_vel) ==="
for i in $(seq 1 15); do ros2 topic pub -1 /cmd_vel geometry_msgs/msg/Twist "{}" >/dev/null 2>&1; done
echo "=== Jetson 노드 종료 ==="
for p in joy_teleop joy_linux teleop_twist_joy slam_toolbox ekf_node sensor_conditioner scan_deskew rplidar_node realsense2_camera "base.launch" "sensors.launch"; do pkill -f "$p" 2>/dev/null; done
sleep 2
echo "=== micro-ROS agent 종료 ==="
docker rm -f microros_agent >/dev/null 2>&1 && echo "agent 종료됨" || echo "agent 이미 없음"
sleep 2
echo "=== 확인 ==="
REMAIN=$(ros2 node list 2>/dev/null | grep -vE '^$' | tr '\n' ' ')
echo "남은 노드: ${REMAIN:-없음(정상 종료)}"
echo "완료 — 로버 손으로 옮겨 충전 가능"
