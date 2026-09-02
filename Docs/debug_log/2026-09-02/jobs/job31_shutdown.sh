#!/bin/bash
# 안전 종료: 모터 정지 → Jetson 노드 → agent. (펌웨어/보드 무관)
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "=== 모터 정지 ==="
for i in $(seq 1 12); do ros2 topic pub -1 /cmd_vel geometry_msgs/msg/Twist "{}" >/dev/null 2>&1; done
echo "=== Nav2/센서/slam 종료 ==="
pkill -9 -f "ros2 launch" 2>/dev/null
for p in controller_server planner_server bt_navigator behavior_server velocity_smoother smoother_server waypoint_follower lifecycle_manager slam_toolbox ekf_node sensor_conditioner scan_deskew rplidar realsense foxglove robot_state_publisher joy_linux teleop component_container; do pkill -9 -f "$p" 2>/dev/null; done
sleep 3
echo "=== agent 종료 ==="
docker rm -f microros_agent >/dev/null 2>&1 && echo "agent 종료됨" || echo "agent 이미 없음"
sleep 2
REMAIN=$(ros2 node list 2>/dev/null | tr '\n' ' ')
echo "남은 노드: ${REMAIN:-없음(정상 종료)}"
echo -n "배터리(마지막): "; echo "측정불가(agent 종료됨)"
echo "완료 — 충전 진행하셔도 됩니다"
