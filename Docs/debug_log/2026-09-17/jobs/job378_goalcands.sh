#!/bin/bash
export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml
source /opt/ros/humble/setup.bash
echo "=== BT 로드 확인 ==="; echo "  TruncatePath 노드: $(grep -c '<TruncatePath' ~/ros2_ws/install/rover_navigation/share/rover_navigation/config/nav_to_pose_no_spin.xml)  bt_navigator 오류: $(grep -a 'bt_navigator' /tmp/nav2.log | grep -aci 'error\|exception\|not registered')"
grep -a "bt_navigator" /tmp/nav2.log | grep -ai "error\|exception\|registered" | tail -2 | cut -c1-160
echo "=== 목표 후보 풋프린트 여유 (≥0.20) ==="
for g in "2.2 0.0" "2.0 0.0" "1.9 0.0" "2.0 0.2" "2.1 0.3" "2.2 0.3" "2.0 -0.2"; do printf "  %-9s " "$g"; python3 /tmp/job377_goalclear.py $g 2>&1 | grep -a "목표 map" | sed 's/목표 map //'; done
