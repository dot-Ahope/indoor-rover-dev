#!/bin/bash
# 09-30 §11: 매핑 모드 prep 상태 확인
for p in rplidar realsense2_camera ekf_node sensor_conditioner async_slam_toolbox stuck_monitor controller_server nvblox_node foxglove_bridge joy_linux; do printf "  %-20s %s
" $p "$(pgrep -fc $p)"; done
echo "== slam.log"; grep -aE "이어 그리기|새 지도|Load From File|error|Error|fail" /tmp/slam.log | head -5 | cut -c1-150; ls -la /tmp/slam.log /tmp/sensors.log /tmp/nav2.log 2>&1 | cut -c20-
echo "== 실시간 로그 prep 부분 끝"; awk "/시작 \| job707/{f=1} f" /tmp/live/current.log | head -30
