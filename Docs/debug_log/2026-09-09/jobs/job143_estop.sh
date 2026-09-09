#!/bin/bash
# 즉시 정지: 지령 발행 주체부터 죽이고 0 지령을 반복 발행
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
for p in "navigation_launch" "controller_server" "bt_navigator" "behavior_server" "velocity_smoother" "planner_server" "smoother_server" "waypoint_follower" "lifecycle_manager_navigation" "stuck_monitor"; do
  pkill -9 -f "$p" 2>/dev/null
done
for i in $(seq 1 25); do ros2 topic pub -1 /cmd_vel geometry_msgs/msg/Twist "{}" >/dev/null 2>&1; done
sleep 1
echo "정지 지령 발행 완료"
echo "cmd_vel 발행자: $(ros2 topic info /cmd_vel 2>/dev/null | grep -a 'Publisher count')"
echo "보드 상태:"
timeout 6 ros2 topic echo /rover/status --once 2>/dev/null | grep -aE "message:|value:" | head -4
echo "휠 속도:"
timeout 5 ros2 topic echo /wheel_odom --once 2>/dev/null | grep -aA1 "twist:" | head -6
