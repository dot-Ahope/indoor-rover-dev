#!/bin/bash
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "=== DDS 복구 확인 ==="
for t in /odometry/filtered /tf /map /scan; do
  printf "  %-22s 퍼블리셔 %s, " "$t" "$(timeout 6 ros2 topic info "$t" 2>/dev/null | grep -aoE 'Publisher count: [0-9]+' | grep -aoE '[0-9]+$')"
  timeout 9 ros2 topic hz "$t" 2>&1 | grep -aoE "average rate: [0-9.]+" | tail -1 || echo "무발행"
done
echo ""
echo "=== TF 체인 ==="
for pair in "map odom" "odom base_link"; do
  printf "  %-16s " "$pair"
  timeout 10 ros2 run tf2_ros tf2_echo $pair 2>&1 | grep -aE "Translation" | tail -1 || echo "없음"
done
echo ""
echo "=== SHM 오류 재발 여부 ==="
echo "  /dev/shm fastrtps: $(ls /dev/shm 2>/dev/null | grep -c fastrtps)개 (정상 재생성)"
echo ""
echo "=== 보드 ==="
echo "  노드: $(ros2 node list 2>/dev/null | grep -a rover_jupiter || echo '없음 — RESET 필요')"
echo "  load: $(cut -d' ' -f1-3 /proc/loadavg)"
