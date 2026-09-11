#!/bin/bash
# 코스 주행 + Nav2 복귀 — 복구 동작(BackUp)이 살아난 뒤 첫 시험
set +u
NAME=${1:-cr1}
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "################ 코스 주행 ################"
bash /tmp/job268_run3.sh $NAME 2>&1 | sed 's/S4 3\/3/코스 주행/'
echo
echo "################ Nav2 복귀 ################"
MARK=$(wc -l < /tmp/nav2.log)
python3 /tmp/job207_return.py 0.0 0.0 0 150 2>&1 | grep -aE "현재 map|결과|최종" | sed 's/^/  /'
tail -n +$((MARK+1)) /tmp/nav2.log > /tmp/ret.log
for pat in "detected collision" "clear except" "clear entirely" "Running backup" "backup completed" "backup failed" "Running wait" "STUCK" "Goal succeeded" "Goal canceled" "Goal failed"; do
  c=$(grep -ac "$pat" /tmp/ret.log); [ "$c" != "0" ] && printf "  %-20s %s건\n" "$pat" "$c"
done
grep -a "STUCK" /tmp/ret.log | tail -1 | cut -c1-140 | sed 's/^/  /'
echo "  EKF 위반 $(grep -ac 'Failed to meet update rate' /tmp/sensors.log)회 | slam 폐기 $(grep -ac 'Message Filter dropping' /tmp/slam.log)회 | load $(cut -d' ' -f1-3 /proc/loadavg)"
