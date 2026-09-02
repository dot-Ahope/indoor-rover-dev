#!/bin/bash
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
pkill -f rot.py 2>/dev/null; sleep 1
echo "=== 프로세스 식별 ==="
DPID=$(pgrep -f scan_deskew | head -1); CPID=$(pgrep -f sensor_conditioner | head -1)
echo "  scan_deskew pid=$DPID"; echo "  sensor_conditioner pid=$CPID"
echo "=== 가벼운 회전(ros2 topic pub, 12s) 백그라운드 + deskew CPU 측정 ==="
setsid nohup bash -c "timeout 12 ros2 topic pub /cmd_vel geometry_msgs/msg/Twist '{angular: {z: 0.6}}' -r 20" > /tmp/pub.log 2>&1 &
sleep 2
echo -n "  회전 중 ω 확인: "; timeout 3 ros2 topic echo /odometry/filtered --once 2>/dev/null | grep -aA3 "twist:" | grep -aoE "z: [-0-9.]+" | tail -1
echo "  deskew CPU 샘플(8s):"
top -b -n 8 -d 1 -p ${DPID:-1} 2>/dev/null | awk -v p=${DPID:-1} '$1==p{print "    "$9"%"; s+=$9; c++} END{if(c)printf "  → deskew 평균=%.1f%% (%d샘플)\n",s/c,c}'
sleep 3
echo "=== 정지 ==="
for i in $(seq 1 10); do ros2 topic pub -1 /cmd_vel geometry_msgs/msg/Twist "{}" >/dev/null 2>&1; done
echo "=== 최종 상위 CPU (회전 종료 후) ==="
top -b -n2 -d1 -o %CPU | awk '/PID +USER/{f++} f==2' | head -7 | awk '{printf "    %-16s %5s%%\n",$12,$9}'
echo "  load: $(cat /proc/loadavg | cut -d' ' -f1-3)"
