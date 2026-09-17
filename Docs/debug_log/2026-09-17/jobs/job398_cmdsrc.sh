#!/bin/bash
export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml
source /opt/ros/humble/setup.bash
echo "=== $(date +%T) /cmd_vel 발행자 ==="; timeout 8 ros2 topic info -v /cmd_vel 2>/dev/null | grep -aE "Node name|Publisher count|Subscription count" | tr -s ' ' | tr '\n' ' '; echo
echo "=== /cmd_vel 샘플 3 s ==="; timeout 3 ros2 topic echo /cmd_vel 2>/dev/null | grep -aE "^  x:|^  z:" | paste - - - - - - 2>/dev/null | awk '{print "lin.x",$2," ang.z",$12}' | sort | uniq -c | head -8
echo "=== /cmd_vel_nav(컨트롤러 출력) 샘플 2 s ==="; timeout 2 ros2 topic echo /cmd_vel_nav 2>/dev/null | grep -aE "^  x:|^  z:" | paste - - - - - - 2>/dev/null | awk '{print "lin.x",$2," ang.z",$12}' | sort | uniq -c | head -4
echo "=== 보드 상태 ==="; timeout 4 ros2 topic echo /rover/status --once 2>/dev/null | grep -aE "key|value" | tr -s ' ' | paste - - | head -3 | cut -c1-200
echo "=== nav2 활성 목표 / 최근 로그 ==="; tail -5 /tmp/nav2.log | cut -c1-170
echo "=== 실행 중 스크립트 ==="; ps -eo pid,etimes,args | grep -aE "python3 /tmp/job|ros2 topic pub|ros2 bag" | grep -av grep | cut -c1-120
