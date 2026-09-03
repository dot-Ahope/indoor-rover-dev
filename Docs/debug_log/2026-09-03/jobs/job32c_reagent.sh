#!/bin/bash
# 보드 재부팅(플래시) 후 agent 재연결 + 데드밴드 재측정
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
docker rm -f microros_agent >/dev/null 2>&1
pkill -f "base.launch" 2>/dev/null; sleep 2
setsid nohup ros2 launch rover_bringup base.launch.py > /tmp/base.log 2>&1 &
sleep 12
echo -n "보드 재연결: "; timeout 6 ros2 topic hz /wheel_odom 2>&1 | grep -aoE "average rate: [0-9.]+" | head -1 || echo "실패!"
pkill -f sensor_conditioner; pkill -f ekf_node; sleep 2
setsid nohup ros2 launch rover_bringup ekf.launch.py > /tmp/ekf.log 2>&1 &
sleep 15
grep -a "gyro bias" /tmp/ekf.log | tail -1
echo -n "/odometry/filtered: "; timeout 5 ros2 topic hz /odometry/filtered 2>&1 | grep -aoE "average rate: [0-9.]+" | head -1
