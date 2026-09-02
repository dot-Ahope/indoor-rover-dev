#!/bin/bash
# 현재 실제 상태 사실확인: 배포 URDF yaw, RSP 노드 수, TF, robot_description 파라미터
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "===배포된 install URDF lidar_joint rpy==="
grep -A3 'name="lidar_joint"' ~/ros2_ws/install/rover_description/share/rover_description/urdf/rover.urdf | grep origin
echo "===src URDF lidar_joint rpy==="
grep -A4 'name="lidar_joint"' ~/ros2_ws/src/rover_description/urdf/rover.urdf | grep origin
echo "===robot_state_publisher 프로세스 수==="
pgrep -af robot_state_publisher | wc -l; pgrep -af robot_state_publisher | cut -c1-70
echo "===실제 TF base_link→lidar_link==="
timeout 5 ros2 run tf2_ros tf2_echo base_link lidar_link 2>&1 | grep -aE "Translation|RPY \(degree\)" | head -2
echo "===파라미터 robot_description 내 lidar yaw (실행중 노드가 쥔 값)==="
ros2 param get /robot_state_publisher robot_description 2>/dev/null | grep -o 'lidar_joint.*' | head -1 | cut -c1-40 || echo "param 조회 실패"
ros2 topic echo /robot_description --once 2>/dev/null | grep -oA0 'lidar' >/dev/null && echo "robot_description 토픽 존재"
echo "===/tf_static 에 실린 lidar_link 회전==="
timeout 6 ros2 topic echo /tf_static --once --qos-durability transient_local 2>/dev/null | grep -B2 -A6 "lidar_link" | grep -E "child_frame|w:|z:" | head -6
echo "===foxglove_bridge 재시작 시각(캐시 의심)==="
pgrep -af foxglove | cut -c1-50
