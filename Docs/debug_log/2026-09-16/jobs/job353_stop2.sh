#!/bin/bash
# 전체 정지(타임아웃 있는 판): 옛 참가자 매칭 대기(ros2 topic pub -1) 를 쓰지 않는다. 로버는 정지 상태(펌웨어 watchdog 500 ms).
export FASTRTPS_DEFAULT_PROFILES_FILE=$HOME/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml
source /opt/ros/humble/setup.bash
pkill -TERM -f "ros2 launch" 2>/dev/null
for p in navigation_launch controller_server planner_server bt_navigator behavior_server velocity_smoother smoother_server waypoint_follower lifecycle_manager stuck_monitor slam_toolbox ekf_node sensor_conditioner scan_deskew rplidar realsense foxglove robot_state_publisher depth_relay; do pkill -TERM -f "$p" 2>/dev/null; done
for i in $(seq 1 15); do [ "$(pgrep -fc 'ekf_node|slam_toolbox|realsense|rplidar|controller_server|robot_state_publisher|depth_relay' 2>/dev/null || echo 0)" = "0" ] && break; sleep 1; done
echo "  잔존: $(pgrep -fc 'ekf_node|slam_toolbox|realsense|rplidar|controller_server|robot_state_publisher|depth_relay' 2>/dev/null || echo 0)"
docker rm -f microros_agent >/dev/null 2>&1 && echo "  agent 종료" || echo "  agent 없음"
ros2 daemon stop >/dev/null 2>&1; sleep 2; rm -f /dev/shm/fastrtps_* /dev/shm/sem.fastrtps_* 2>/dev/null
echo "  ROS 프로세스: $(ps -eo args 2>/dev/null | grep -aiE 'opt/ros|ros2_ws' | grep -avc grep)   docker: $(docker ps -q | wc -l)"
