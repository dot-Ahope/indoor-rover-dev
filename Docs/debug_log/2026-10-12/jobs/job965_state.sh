#!/bin/bash
# 10-12 §5.3: 주행 중단 뒤 정지 상태에서 포화가 남아 있는가 — /tf 주기, 프로세스 CPU, 루프백 패킷. 로버 안 움직임
echo "  시각 $(date +%T) · 부하 $(cut -d' ' -f1-3 /proc/loadavg)"
top -b -n1 | head -22 | tail -16 | awk '{printf "    %-18s %5s %%\n", $12, $9}' | head -14
a=$(awk '/lo:/{print $3, $11}' /proc/net/dev); sleep 5; b=$(awk '/lo:/{print $3, $11}' /proc/net/dev)
echo "  루프백 패킷/s: 수신 $(( ($(echo $b | cut -d' ' -f1) - $(echo $a | cut -d' ' -f1)) / 5 )) 송신 $(( ($(echo $b | cut -d' ' -f2) - $(echo $a | cut -d' ' -f2)) / 5 ))"
echo "  /tf: $(timeout 10 ros2 topic hz /tf 2>&1 | grep -aoE 'average rate: [0-9.]+' | tail -1) · $(timeout 10 ros2 topic bw /tf 2>&1 | grep -aE 'B/s|bytes' | tail -1 | cut -c1-80)"
echo "  Nav2 목표 상태: $(timeout 8 ros2 topic echo --once /navigate_to_pose/_action/status 2>/dev/null | grep -a 'status:' | tail -1)"
