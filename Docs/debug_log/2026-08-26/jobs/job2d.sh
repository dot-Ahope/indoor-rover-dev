#!/bin/bash
# Step 2 재검증: agent 세션 재수립 확인 + 토픽 주기
source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash
echo "===AGENT_SESSION_LOG==="
grep -aE "session established|create_client" /tmp/bringup.log | tail -3 || echo NO_SESSION_YET
echo "===TOPIC_LIST==="
ros2 topic list
echo "===HZ_WHEEL_ODOM==="
timeout 10 ros2 topic hz /wheel_odom 2>&1 | tail -2 || true
echo "===HZ_IMU==="
timeout 10 ros2 topic hz /imu/data_raw 2>&1 | tail -2 || true
echo "===NODE_LIST==="
ros2 node list
