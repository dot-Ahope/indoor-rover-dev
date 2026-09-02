#!/bin/bash
source /opt/ros/humble/setup.bash 2>/dev/null
echo "=== 중복 인스턴스 확인 ==="
echo "  scan_deskew: $(pgrep -f scan_deskew | tr '\n' ' ') (개수 $(pgrep -f scan_deskew|wc -l))"
echo "  sensor_conditioner: $(pgrep -f sensor_conditioner | tr '\n' ' ') (개수 $(pgrep -f sensor_conditioner|wc -l))"
echo "  foxglove_bridge: $(pgrep -f foxglove_bridge | wc -l)개"
echo "=== 상위 CPU + python3 정체 ==="
top -b -n2 -d1 -o %CPU | awk '/PID +USER/{f++} f==2' | head -9 > /tmp/t.txt
awk '{printf "  pid=%-6s cpu=%5s%% cmd=%s\n",$1,$9,$12}' /tmp/t.txt
echo "=== python3 PID별 실체 (cmdline) ==="
for pid in $(awk '$12=="python3"{print $1}' /tmp/t.txt); do
  echo "  [$pid] $(cat /proc/$pid/cmdline 2>/dev/null | tr '\0' ' ' | grep -aoE '[^ ]*\.py[^ ]*|scan_deskew|sensor_conditioner' | head -1)"
done
