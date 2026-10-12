#!/bin/bash
# 10-12 §3.2: 전역 정적 층이 지도를 못 받는 원인 — map_server 상태·/map_nav 발행·로그. 로버 안 움직임
echo "  map_server 프로세스: $(pgrep -fa map_server | cut -c1-200)"
ros2 node list 2>/dev/null | grep -iE "map|lifecycle" | tr '\n' ' '; echo
for n in /map_server /nav_map_server /map_server_nav; do r=$(timeout 8 ros2 lifecycle get $n 2>&1 | tail -1); echo "  $n: $r"; done
timeout 8 ros2 topic info -v /map_nav 2>&1 | grep -aE "Node name|Durability|Reliability|Publisher count|Subscription count" | tr '\n' ' ' | cut -c1-400; echo
grep -aiE "map_server|map_nav|lifecycle_manager_map|yaml|Loading|Failed|rror" /tmp/nav2.log | grep -av "Message Filter\|NvbloxCostmapLayer" | head -20 | cut -c1-220
echo "  지도 파일: $(ls -la /home/jetson/maps/office/office_v3.yaml /home/jetson/maps/office/office_v3.pgm 2>&1 | awk '{print $5, $9}' | tr '\n' ' ')"
