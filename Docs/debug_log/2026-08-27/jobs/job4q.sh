#!/bin/bash
# EKF debug 모드 15s: imu0 측정이 처리되는지 / TF 변환 실패 여부 직접 확인
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
Y=~/ros2_ws/install/rover_bringup/share/rover_bringup/config/ekf.yaml
pkill -f ekf_node 2>/dev/null; sleep 1
rm -f /tmp/ekf_debug.txt
timeout 15 ros2 run robot_localization ekf_node --ros-args -r __node:=ekf_filter_node --params-file $Y \
  -p debug:=true -p debug_out_file:=/tmp/ekf_debug.txt > /tmp/ekf_dbg_stdout.log 2>&1
echo "===DEBUG FILE SIZE==="; wc -lc /tmp/ekf_debug.txt
echo "===topic mentions==="; grep -aoE "imu0[_a-z]*|odom0[_a-z]*" /tmp/ekf_debug.txt | sort | uniq -c | sort -rn | head -8
echo "===transform / ignore / drop lines==="; grep -aiE "could not|ignor|drop|older|unavailable|transform" /tmp/ekf_debug.txt | sort | uniq -c | sort -rn | head -8
echo "===imu0 callback context (first)==="; grep -an -A12 "imu0_twist" /tmp/ekf_debug.txt | head -40 | cut -c1-160
echo "===stdout warnings==="; grep -aiE "warn|error" /tmp/ekf_dbg_stdout.log | head -5 | cut -c1-200
echo "===RESTORE ekf launch==="
pkill -f "ekf.launch" 2>/dev/null; pkill -f sensor_conditioner 2>/dev/null; sleep 1
setsid nohup ros2 launch rover_bringup ekf.launch.py > /tmp/ekf.log 2>&1 &
sleep 5; pgrep -af "ekf_node|sensor_conditioner" | wc -l
