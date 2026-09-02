#!/bin/bash
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
DPID=$(pgrep -f scan_deskew | head -1)
echo "=== BEFORE ==="
echo "  deskew(pid $DPID) CPU: $(top -b -n2 -d1 -p ${DPID:-1} 2>/dev/null | tail -1 | awk '{print $9}')%"
echo "  load: $(cat /proc/loadavg | cut -d' ' -f1-3)"
echo "=== 소스 갱신·재빌드 ==="
cp /tmp/scan_deskew.py ~/ros2_ws/src/rover_bringup/scripts/scan_deskew.py
cp /tmp/foxglove.launch.py ~/ros2_ws/src/rover_bringup/launch/foxglove.launch.py
cd ~/ros2_ws && colcon build --packages-select rover_bringup 2>&1 | tail -2
source ~/ros2_ws/install/setup.bash
echo "=== scan_deskew 재시작 ==="
pkill -f scan_deskew; sleep 2
setsid nohup ros2 run rover_bringup scan_deskew.py --ros-args -p ref:=end -p omega_deadband:=0.02 > /tmp/deskew.log 2>&1 &
echo "=== foxglove 재시작(whitelist 적용) ==="
pkill -f foxglove; sleep 2
setsid nohup ros2 launch rover_bringup foxglove.launch.py > /tmp/fg.log 2>&1 &
sleep 9
echo "=== 검증 ==="
echo -n "  /scan: "; timeout 5 ros2 topic hz /scan 2>&1 | grep -aoE "average rate: [0-9.]+" | head -1 || echo "무발행!"
echo "  노드: $(ros2 node list 2>/dev/null | grep -E 'scan_deskew|foxglove' | tr '\n' ' ')"
echo -n "  whitelist 적용: "; ros2 param get /foxglove_bridge topic_whitelist 2>/dev/null | tr '\n' ' ' | grep -aoE "scan.*joy|/scan" | head -1 && echo "(설정됨)" || echo "?"
DPID2=$(pgrep -f scan_deskew | head -1)
echo "=== AFTER ==="
echo "  deskew(pid $DPID2) CPU: $(top -b -n2 -d1 -p ${DPID2:-1} 2>/dev/null | tail -1 | awk '{print $9}')%"
echo "  상위 CPU:"; top -b -n2 -d1 -o %CPU | awk '/PID +USER/{f++} f==2' | head -7 | awk '{printf "    %-16s %5s%%\n",$12,$9}'
echo "  load: $(cat /proc/loadavg | cut -d' ' -f1-3)"
