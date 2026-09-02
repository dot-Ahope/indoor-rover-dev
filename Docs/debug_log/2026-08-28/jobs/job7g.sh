#!/bin/bash
# 재부팅 vs WiFi 단절 판별 + 스택/세션 생존 확인
echo "===UPTIME (짧으면 재부팅)==="; uptime; echo "부팅시각: $(uptime -s)"; echo "현재시각: $(date '+%F %T')"
echo "===전원/재부팅 흔적 (dmesg 최근)==="; echo '<PW>' | sudo -S -p '' dmesg 2>/dev/null | tail -6 | cut -c1-100
echo "===지난 재부팅 이력==="; last -x 2>/dev/null | grep -iE "reboot|shutdown" | head -3 || echo "last 없음"
echo "===ROS 노드 생존 (재시작 안됐으면 그대로 있음)==="
source /opt/ros/humble/setup.bash 2>/dev/null; source ~/ros2_ws/install/setup.bash 2>/dev/null
pgrep -af "robot_state_publisher|ekf_node|slam_toolbox|realsense2_camera_node|rplidar_node|foxglove" | wc -l
echo "  실행중: $(ros2 node list 2>/dev/null | tr '\n' ' ')"
echo "===agent 컨테이너 uptime (재부팅이면 사라지거나 재시작)==="; docker ps --format '{{.Names}} {{.Status}}' | grep microros || echo NO_AGENT
echo "===보드 세션 (토픽)==="; echo -n "wheel_odom: "; timeout 6 ros2 topic hz /wheel_odom 2>&1 | grep -aE "average|does not" | tail -1
echo -n "battery: "; timeout 5 ros2 topic echo /battery --once --field voltage 2>/dev/null || echo NONE
echo "===HID 모듈 (재부팅시 자동로드 확인)==="; lsmod | grep -c hid_sensor
echo "===WiFi 신호==="; iwconfig wlP1p1s0 2>/dev/null | grep -iE "signal|link quality" || nmcli -f SIGNAL,SSID dev wifi 2>/dev/null | head -2
