#!/bin/bash
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo -n "종료 전 배터리: "; timeout 6 ros2 topic echo /battery --once 2>/dev/null | grep -aoE "voltage: [0-9.]+" | head -1
echo "=== 모터 정지 ==="
for i in $(seq 1 12); do ros2 topic pub -1 /cmd_vel geometry_msgs/msg/Twist "{}" >/dev/null 2>&1; done
echo "=== 노드 종료 ==="
pkill -9 -f "ros2 launch" 2>/dev/null
for p in navigation_launch controller_server planner_server bt_navigator behavior_server velocity_smoother smoother_server waypoint_follower lifecycle_manager stuck_monitor slam_toolbox ekf_node sensor_conditioner scan_deskew rplidar realsense foxglove robot_state_publisher joy_linux teleop component_container; do pkill -9 -f "$p" 2>/dev/null; done
sleep 4
echo "=== agent 종료 ==="
docker rm -f microros_agent >/dev/null 2>&1 && echo "  agent 종료됨" || echo "  agent 이미 없음"
sleep 2
echo "남은 노드: $(ros2 node list 2>/dev/null | tr '\n' ' ')"
echo "남은 ROS 프로세스: $(pgrep -fc 'ekf_node|slam_toolbox|realsense|rplidar|controller_server|foxglove|stuck_monitor' 2>/dev/null || echo 0)"
echo "docker: $(docker ps -q | wc -l)개"
echo "load: $(cut -d' ' -f1-3 /proc/loadavg)"
