#!/bin/bash
# 09-30 F1: USB 패드 매핑 조종 기동(profile mapping = 0.07 m/s·0.3 rad/s) + 확인
set +u; source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml
ls -la /dev/input/js* 2>&1 | head -3
pkill -f joy_linux_node; pkill -f teleop_node; sleep 1
: > /tmp/joy.log; setsid nohup ros2 launch rover_bringup joy_teleop.launch.py profile:=mapping > /tmp/joy.log 2>&1 < /dev/null &
sleep 6
echo "  /joy: $(timeout 5 ros2 topic hz /joy 2>&1 | grep -aoE 'average rate: [0-9.]+' | tail -1)"
for p in scale_linear.x scale_angular.yaw require_enable_button; do echo "  $p = $(timeout 8 ros2 param get /teleop_twist_joy_node $p 2>&1 | tail -1)"; done
grep -aiE "error|could not|fail" /tmp/joy.log | head -3
