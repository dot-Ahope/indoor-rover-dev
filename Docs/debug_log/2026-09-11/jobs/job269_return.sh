#!/bin/bash
set +u
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
MARK=$(wc -l < /tmp/nav2.log)
echo "=== 복귀 (Nav2 → 원점 0,0,0°) ==="
python3 /tmp/job207_return.py 0.0 0.0 0 120 2>&1 | grep -aE "현재 map|결과|최종" | sed 's/^/  /'
echo "=== 복귀 중 로그 ==="
tail -n +$((MARK+1)) /tmp/nav2.log > /tmp/ret.log
for pat in "detected collision" "clear except" "clear entirely" "backup" "STUCK" "Goal succeeded" "Goal canceled" "Goal failed"; do
  c=$(grep -ac "$pat" /tmp/ret.log); [ "$c" != "0" ] && printf "  %-20s %s건\n" "$pat" "$c"
done
grep -a "STUCK" /tmp/ret.log | tail -1 | cut -c1-130 | sed 's/^/  /'
echo "  상자 (로버 기준): $(python3 /tmp/job248_audit.py 2>&1 | grep -a '^상자:' | head -1 | cut -c1-60)"
echo "  EKF 위반 $(grep -ac 'Failed to meet update rate' /tmp/sensors.log)회 | slam 폐기 $(grep -ac 'Message Filter dropping' /tmp/slam.log)회 | load $(cut -d' ' -f1-3 /proc/loadavg)"
