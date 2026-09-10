#!/bin/bash
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "=== foxglove 클라이언트 연결 여부 ==="
ss -tn 2>/dev/null | grep -a ":8765" | head -3 | sed 's/^/  /' || echo "  연결 없음"
echo "=== foxglove_bridge 정지 ==="
pkill -TERM -f foxglove_bridge 2>/dev/null; sleep 3
echo "  프로세스: $(pgrep -fc foxglove_bridge 2>/dev/null | head -1)"
echo ""
echo "=== 30초 재측정 ==="
A_EKF=$(grep -ac 'Failed to meet update rate' /tmp/sensors.log 2>/dev/null)
A_SLAM=$(grep -ac 'Message Filter dropping' /tmp/slam.log 2>/dev/null)
top -b -n 30 -d 1 -o %CPU > /tmp/s6top2.txt 2>/dev/null &
sleep 31; wait 2>/dev/null
B_EKF=$(grep -ac 'Failed to meet update rate' /tmp/sensors.log 2>/dev/null)
B_SLAM=$(grep -ac 'Message Filter dropping' /tmp/slam.log 2>/dev/null)
echo "  EKF 주기 위반 : $((B_EKF-A_EKF)) 회 / 30초"
echo "  slam 스캔 폐기: $((B_SLAM-A_SLAM)) 회 / 30초"
echo "  load: $(cut -d' ' -f1-3 /proc/loadavg)"
awk '/^ *[0-9]+ / {cpu[$12]+=$9; n[$12]++} END {for (c in cpu) printf "  %-18s %6.1f%%\n", c, cpu[c]/n[c]}' /tmp/s6top2.txt | sort -k2 -rn | head -7
echo ""
echo "=== Nav2 상태 ==="
for nd in /controller_server /planner_server /bt_navigator /behavior_server /velocity_smoother; do
  printf "  %-20s " "$nd"; timeout 6 ros2 lifecycle get "$nd" 2>/dev/null || echo "?"
done
