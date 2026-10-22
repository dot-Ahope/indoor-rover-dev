#!/bin/bash
# 10-22 §12 정지 확인: 휠 속도 · 남은 bag 기록기 정상 종료(SIGINT) · bag 크기
source /opt/ros/humble/setup.bash
timeout 4 ros2 topic echo --once /wheel_odom 2>/dev/null | grep -A3 "twist:" | grep -E "x:|z:" | head -4
echo "기록기: $(pgrep -fa 'ros2 bag record' | grep -c f2lp1)"; pkill -INT -f "bag record.*f2lp1"; sleep 4; echo "기록기 남음: $(pgrep -fa 'ros2 bag record' | grep -c f2lp1)"
du -sh /tmp/bag_f2lp1 2>/dev/null; ls /tmp/bag_f2lp1 2>/dev/null | head
