#!/bin/bash
# S6 기준선: Nav2 포함 상태에서 EKF 주기 위반 / slam 스캔 폐기 / 노드별 CPU 를 30초 창으로 잰다.
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
: > /tmp/nav2.log
setsid nohup ros2 launch rover_navigation navigation.launch.py > /tmp/nav2.log 2>&1 &
sleep 32
echo "=== Nav2 상태 ==="
for nd in /controller_server /planner_server /bt_navigator /behavior_server; do
  printf "  %-20s " "$nd"; timeout 6 ros2 lifecycle get "$nd" 2>/dev/null || echo "?"
done
echo "  레이어: $(timeout 8 ros2 param get /local_costmap/local_costmap plugins 2>/dev/null | sed 's/^.*is: //')"
echo ""
echo "=== 30초 측정 시작 ==="
A_EKF=$(grep -ac 'Failed to meet update rate' /tmp/sensors.log 2>/dev/null)
A_SLAM=$(grep -ac 'Message Filter dropping' /tmp/slam.log 2>/dev/null)
top -b -n 30 -d 1 -o %CPU > /tmp/s6top.txt 2>/dev/null &
TOPPID=$!
sleep 31
wait $TOPPID 2>/dev/null
B_EKF=$(grep -ac 'Failed to meet update rate' /tmp/sensors.log 2>/dev/null)
B_SLAM=$(grep -ac 'Message Filter dropping' /tmp/slam.log 2>/dev/null)
echo "  EKF 주기 위반 : $((B_EKF-A_EKF)) 회 / 30초   ← 종료조건 0"
echo "  slam 스캔 폐기: $((B_SLAM-A_SLAM)) 회 / 30초  ← 종료조건 0"
echo "  load: $(cut -d' ' -f1-3 /proc/loadavg)         ← 종료조건 < 6"
echo ""
echo "=== 30초 평균 CPU (상위) ==="
awk '/^ *[0-9]+ / {cpu[$12]+=$9; n[$12]++} END {for (c in cpu) printf "  %-18s %6.1f%%\n", c, cpu[c]/n[c]}' /tmp/s6top.txt | sort -k2 -rn | head -10
echo ""
echo "=== 토픽 주기 ==="
for t in /imu/data /camera/camera/imu /odometry/filtered /tf /map /scan; do
  printf "  %-24s " "$t"; timeout 9 ros2 topic hz "$t" 2>&1 | grep -aoE "average rate: [0-9.]+" | tail -1 || echo 무발행
done
echo "  배터리: $(timeout 5 ros2 topic echo /battery --once 2>/dev/null | grep -aoE 'voltage: [0-9.]+')"
