#!/bin/bash
# 보드 세션 진단: agent 상태, wheel_odom 실측, battery, heartbeat
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "===agent 컨테이너==="; docker ps --format '{{.Names}} {{.Status}}' | grep microros || echo NO_AGENT
echo "===agent 최근 로그==="; docker logs --tail 3 microros_agent 2>&1 | grep -aE "session|Serial|error" | tail -3
echo "===토픽 존재==="; ros2 topic list | grep -E "wheel_odom|battery|heartbeat|rover" | tr '\n' ' '; echo
echo "===wheel_odom 10s hz==="; timeout 10 ros2 topic hz /wheel_odom 2>&1 | grep -aE "average|does not" | tail -1
echo "===battery==="; timeout 6 ros2 topic echo /battery --once --field voltage 2>/dev/null || echo NO_BATTERY
echo "===heartbeat==="; timeout 6 ros2 topic echo /rover/f5b_heartbeat --once 2>/dev/null || echo NO_HB
echo "===imu_data_raw (보드 IMU, 세션 살아있으면 나옴)==="; timeout 5 ros2 topic hz /imu/data_raw 2>&1 | grep -aE "average|does not" | tail -1
