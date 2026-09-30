#!/bin/bash
# 09-30 §4 F1: prep(새 지도) → 패드 장치 확인 → 끊김 시험용 조종(출력 /cmd_vel_test, 로버 비구동)
set +u
bash /tmp/job657_prep_f0b.sh 2>&1 | grep -aE "wheel_odom|gyro bias|odometry/filtered|map->odom|_server|slam 인자|icr|배터리"
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml
echo "== 패드 장치"; ls -la /dev/input/js* 2>&1 | head -3; grep -aiE "dragon|gamepad|joystick|xbox|controller" /proc/bus/input/devices | head -3
CFG=~/ros2_ws/install/rover_bringup/share/rover_bringup/config/joy_teleop.yaml
pkill -f joy_linux_node; pkill -f teleop_node; sleep 1
setsid nohup ros2 run joy_linux joy_linux_node --ros-args -r __node:=joy_node --params-file $CFG > /tmp/joy_test.log 2>&1 < /dev/null &
setsid nohup ros2 run teleop_twist_joy teleop_node --ros-args -r __node:=teleop_twist_joy_node --params-file $CFG -p scale_linear.x:=0.07 -p scale_angular.yaw:=0.3 -r cmd_vel:=/cmd_vel_test >> /tmp/joy_test.log 2>&1 < /dev/null &
sleep 6
echo "  /joy: $(timeout 5 ros2 topic hz /joy 2>&1 | grep -aoE 'average rate: [0-9.]+' | tail -1)"
echo "  teleop 출력 토픽: $(timeout 6 ros2 node info /teleop_twist_joy_node 2>/dev/null | grep -aA3 Publishers | grep -ao '/cmd_vel[_a-z]*' | head -1)"
grep -aiE "error|could not|no such" /tmp/joy_test.log | head -3
