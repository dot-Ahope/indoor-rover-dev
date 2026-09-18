#!/bin/bash
# base(micro-ROS 에이전트 + robot_state_publisher)만 기동 — 이후 사용자 보드 리셋
export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml
source /opt/ros/humble/setup.bash; source /home/jetson/ros2_ws/install/setup.bash
echo "에이전트 컨테이너: $(docker ps --format '{{.Names}}' | grep -c microros_agent), rsp: $(pgrep -fc '[r]obot_state_publisher')"
if [ "$(docker ps --format '{{.Names}}' | grep -c microros_agent)" = "0" ]; then
  docker rm -f microros_agent >/dev/null 2>&1
  setsid nohup ros2 launch rover_bringup base.launch.py > /tmp/base.log 2>&1 &
  sleep 14
fi
echo "에이전트 컨테이너: $(docker ps --format '{{.Names}}' | grep -c microros_agent), rsp: $(pgrep -fc '[r]obot_state_publisher'), 보드 장치: $(ls /dev/rover /dev/ttyUSB0 2>&1 | tr '\n' ' ')"
echo -n "TF base_link←lidar_link yaw: "; timeout 8 ros2 run tf2_ros tf2_echo base_link lidar_link 2>&1 | grep -aE "RPY \(radian\)" | head -1
echo -n "/wheel_odom: "; timeout 6 ros2 topic hz /wheel_odom 2>&1 | grep -aoE "average rate: [0-9.]+" | head -1 || echo "무발행(리셋 필요)"
