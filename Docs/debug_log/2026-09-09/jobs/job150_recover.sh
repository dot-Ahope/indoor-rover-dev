#!/bin/bash
# DDS 공유메모리 잔재 복구. 핵심: SIGKILL 금지 — SIGTERM 으로 정상 종료시켜야
# FastDDS 가 /dev/shm 세그먼트와 잠금 파일을 스스로 정리한다.
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash

NODES="navigation_launch controller_server planner_server bt_navigator behavior_server \
velocity_smoother smoother_server waypoint_follower lifecycle_manager stuck_monitor \
slam_toolbox ekf_node sensor_conditioner scan_deskew rplidar realsense foxglove \
robot_state_publisher"

echo "=== 1) SIGTERM 으로 정상 종료 ==="
pkill -TERM -f "ros2 launch" 2>/dev/null
for p in $NODES; do pkill -TERM -f "$p" 2>/dev/null; done
for i in $(seq 1 12); do
  n=$(pgrep -fc "ekf_node|slam_toolbox|realsense|rplidar|foxglove|sensor_conditioner|robot_state_publisher" 2>/dev/null || echo 0)
  [ "$n" = "0" ] && break
  sleep 1
done
echo "  10초 후 잔존: $(pgrep -fc 'ekf_node|slam_toolbox|realsense|rplidar|foxglove|sensor_conditioner|robot_state_publisher' 2>/dev/null || echo 0)"
echo "=== 2) 남은 것만 SIGKILL (최후수단) ==="
for p in $NODES; do pkill -9 -f "$p" 2>/dev/null; done
sleep 2
echo "=== 3) agent 종료 + ros2 daemon 종료 ==="
docker rm -f microros_agent >/dev/null 2>&1 && echo "  agent 종료" || echo "  agent 없음"
ros2 daemon stop >/dev/null 2>&1; sleep 2
echo "=== 4) /dev/shm FastDDS 잔재 정리 ==="
echo "  정리 전: $(ls /dev/shm 2>/dev/null | wc -l)개 (fastrtps $(ls /dev/shm 2>/dev/null | grep -c fastrtps))"
echo "  아직 /dev/shm 을 여는 프로세스: $(fuser /dev/shm/* 2>/dev/null | tr ' ' '\n' | sort -u | grep -c '[0-9]')"
rm -f /dev/shm/fastrtps_* /dev/shm/sem.fastrtps_* 2>/dev/null
echo "  정리 후: $(ls /dev/shm 2>/dev/null | wc -l)개 (fastrtps $(ls /dev/shm 2>/dev/null | grep -c fastrtps))"
echo "=== 5) 상태 ==="
echo "  ROS 프로세스: $(ps -eo args 2>/dev/null | grep -aiE 'opt/ros|ros2_ws' | grep -avc grep)"
echo "  docker: $(docker ps -q | wc -l)"
echo "  load: $(cut -d' ' -f1-3 /proc/loadavg)"
