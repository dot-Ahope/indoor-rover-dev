#!/bin/bash
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "=== 실제 프로세스 (ros 관련) ==="
ps -eo pid,pcpu,comm,args --sort=-pcpu 2>/dev/null | grep -aiE "ros|nav2|realsense|rplidar|slam|ekf|foxglove|micro" | grep -av grep | head -12 | cut -c1-140
echo ""
echo "=== 개수 ==="
echo "  ros 관련 프로세스: $(ps -eo args 2>/dev/null | grep -aiE 'opt/ros|ros2_ws' | grep -avc grep)"
echo "  docker 컨테이너: $(docker ps -q | wc -l)"
echo ""
echo "=== ros2 daemon 재시작 후 노드 목록 (캐시 제거) ==="
ros2 daemon stop >/dev/null 2>&1; sleep 2; ros2 daemon start >/dev/null 2>&1; sleep 3
echo "  노드: $(timeout 10 ros2 node list 2>/dev/null | tr '\n' ' ')"
echo ""
echo "=== 부하 ==="
echo "  load: $(cut -d' ' -f1-3 /proc/loadavg)"
top -b -n2 -d1 -o %CPU 2>/dev/null | awk '/PID +USER/{f++} f==2' | head -6 | awk '{printf "    %-18s %6s%%\n", $12, $9}'
