#!/bin/bash
# 10-12 §3.2: 지연 적용 뒤에도 unconfigured — 관리 노드 로그와 수동 전이 시도. 로버 안 움직임
echo "  설치본 지연: $(grep -c 'period=3.0' ~/ros2_ws/install/rover_navigation/share/rover_navigation/launch/navigation.launch.py)"
grep -aE "lifecycle_manager_navmap|nav_map_server|map_server-|lifecycle_manager-1[0-9]" /tmp/nav2.log | sed 's/\x1b\[[0-9;]*m//g' | head -20 | cut -c1-220
echo "-- 수동 configure"; timeout 30 ros2 lifecycle set /nav_map_server configure 2>&1 | tail -2
echo "  상태: $(timeout 10 ros2 lifecycle get /nav_map_server 2>&1 | tail -1)"
grep -aE "nav_map_server|map_io|yaml|Failed|rror" /tmp/nav2.log | sed 's/\x1b\[[0-9;]*m//g' | grep -av "NvbloxCostmapLayer\|Message Filter" | tail -8 | cut -c1-220
cat /home/jetson/maps/office/office_v3.yaml
