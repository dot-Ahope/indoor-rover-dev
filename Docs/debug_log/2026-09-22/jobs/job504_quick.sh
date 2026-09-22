#!/bin/bash
# 보드 리셋 직후 빠른 확인(읽기 전용): 에이전트 세션·wheel_odom·스택 프로세스·prep 진행 중인 job 들
export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; source /home/jetson/ros2_ws/install/setup.bash
echo "== 스택: agent $(docker ps --format '{{.Names}}' | grep -c micro) camera $(pgrep -fc realsense2_camera_node) lidar $(pgrep -fc sllidar) relay $(pgrep -fc depth_relay) ekf $(pgrep -fc ekf_node) slam $(pgrep -fc slam_toolbox) controller $(pgrep -fc controller_server) planner $(pgrep -fc planner_server) rsp $(pgrep -fc robot_state_publisher)"
echo "== 진행 중 job: $(ps -eo args | grep -aE '^bash /tmp/job|^python3 /tmp/job' | grep -av grep | cut -c1-40 | tr '\n' ';')"
echo "== wheel_odom: $(timeout 7 ros2 topic hz /wheel_odom 2>&1 | grep -ao 'average rate: [0-9.]*' | head -1 | cut -d' ' -f3) Hz | scan: $(timeout 7 ros2 topic hz /scan 2>&1 | grep -ao 'average rate: [0-9.]*' | head -1 | cut -d' ' -f3) Hz | odom(EKF): $(timeout 7 ros2 topic hz /odometry/filtered 2>&1 | grep -ao 'average rate: [0-9.]*' | head -1 | cut -d' ' -f3) Hz"
echo "== 에이전트 로그 끝: $(docker logs --tail 3 $(docker ps --format '{{.Names}}' | grep micro | head -1) 2>&1 | tr '\n' ' ' | cut -c1-200)"
