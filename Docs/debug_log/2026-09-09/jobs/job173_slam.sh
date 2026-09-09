#!/bin/bash
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "=== slam_toolbox 프로세스/노드 ==="
pgrep -af slam_toolbox | cut -c1-110 | sed 's/^/  /' || echo "  프로세스 없음"
echo "  노드: $(ros2 node list 2>/dev/null | grep -a slam || echo 없음)"
echo "  CPU/상태: $(ps -p $(pgrep -f slam_toolbox | head -1) -o %cpu=,stat=,etime= 2>/dev/null)"
echo ""
echo "=== 발행 여부 ==="
for t in /map /map_metadata /slam_toolbox/graph_visualization; do
  printf "  %-34s " "$t"; timeout 9 ros2 topic hz "$t" 2>&1 | grep -aoE "average rate: [0-9.]+" | tail -1 || echo 무발행
done
echo "  /map 퍼블리셔: $(timeout 6 ros2 topic info /map 2>/dev/null | grep -aoE 'Publisher count: [0-9]+')"
echo ""
echo "=== map→odom 조회 ==="
timeout 12 ros2 run tf2_ros tf2_echo map odom 2>&1 | grep -aE "Translation|does not exist|Invalid" | tail -2 | sed 's/^/  /'
echo ""
echo "=== SHM 상태 ==="
echo "  /dev/shm fastrtps: $(ls /dev/shm 2>/dev/null | grep -c fastrtps)개"
echo "  고아(잠금만 있고 본체 없음):"
for f in $(ls /dev/shm 2>/dev/null | grep -oE '^fastrtps_port[0-9]+' | sort -u); do
  [ ! -f "/dev/shm/$f" ] && [ -f "/dev/shm/${f}_el" ] && echo "    $f"
done
echo ""
echo "=== slam 로그 마지막 ==="
tail -6 /tmp/slam.log | cut -c1-150 | sed 's/^/  /'
