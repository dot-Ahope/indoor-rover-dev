#!/bin/bash
# 리셋 후 재검증: 세션 로그, 토픽, 주기
source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash
echo "===AGENT_SESSION_LOG==="
grep -a "session established" /tmp/bringup.log | tail -2 || echo NO_SESSION_YET
echo "===TOPIC_LIST==="
ros2 topic list
echo "===HZ_WHEEL_ODOM==="
timeout 10 ros2 topic hz /wheel_odom 2>&1 | tail -2 || true
echo "===HZ_IMU==="
timeout 10 ros2 topic hz /imu/data_raw 2>&1 | tail -2 || true
echo "===BATTERY==="
timeout 8 ros2 topic echo /battery --once --field voltage 2>/dev/null || echo NO_BATTERY_MSG
