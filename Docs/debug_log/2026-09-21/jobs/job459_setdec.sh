#!/bin/bash
# 디시메이션 런타임 변경 시험 (S2): realsense-ros 4.x 는 필터 파라미터가 동적이라 재기동 없이 바뀌는지 본다. 인자: DEC
DEC=${1:-2}
export FASTRTPS_DEFAULT_PROFILES_FILE=$HOME/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "전: $(timeout 8 ros2 param get /camera/camera decimation_filter.filter_magnitude 2>&1 | tail -1) | 원시 점군 크기: $(timeout 6 ros2 topic echo /camera/camera/depth/color/points --once --field width 2>/dev/null | head -1)x$(timeout 6 ros2 topic echo /camera/camera/depth/color/points --once --field height 2>/dev/null | head -1)"
timeout 10 ros2 param set /camera/camera decimation_filter.filter_magnitude $DEC 2>&1 | tail -1
sleep 3
echo "후: $(timeout 8 ros2 param get /camera/camera decimation_filter.filter_magnitude 2>&1 | tail -1) | 원시 점군 크기: $(timeout 6 ros2 topic echo /camera/camera/depth/color/points --once --field width 2>/dev/null | head -1)x$(timeout 6 ros2 topic echo /camera/camera/depth/color/points --once --field height 2>/dev/null | head -1)"
echo "원시 hz: $(timeout 8 ros2 topic hz /camera/camera/depth/color/points 2>&1 | grep -ao 'average rate: [0-9.]*' | head -1) | 릴레이 hz: $(timeout 8 ros2 topic hz /camera/depth/points_filtered 2>&1 | grep -ao 'average rate: [0-9.]*' | head -1)"
sleep 5; top -b -n2 -d3 -o %CPU 2>/dev/null | awk '/PID +USER/{f++} f==2' | awk 'NR>1 && ($12 ~ /realsen|depth_re|python3/) {printf "  cpu %-14s %5s%%\n", $12, $9}'
echo "EKF 위반 누적: $(grep -ac 'Failed to meet update rate' /tmp/sensors.log) | load $(cut -d' ' -f1-3 /proc/loadavg)"
