#!/bin/bash
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "=== nav2.log 최근 30줄 (정지 구간 원인) ==="
tail -30 /tmp/nav2.log | grep -avE "^\[INFO\].*process started"
echo ""
echo "=== 반복 패턴 집계 ==="
grep -aoE "Failed to make progress|Aborting handle|missed its desired rate|Behavior [A-Za-z]+ (running|completed)|recovery|No valid path|Costmap.*not|timed out|Timed out" /tmp/nav2.log | sort | uniq -c | sort -rn | head -10
echo ""
echo "=== CPU 확보: foxglove 종료 ==="
pkill -f foxglove; sleep 3
echo "  load(직후): $(cat /proc/loadavg | cut -d' ' -f1-3)"
top -b -n2 -d1 -o %CPU | awk '/PID +USER/{f++} f==2' | head -7 | awk '{printf "    %-16s %5s%%\n",$12,$9}'
