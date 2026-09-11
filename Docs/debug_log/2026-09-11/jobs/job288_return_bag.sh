#!/bin/bash
# Nav2 복귀 + bag + 로그 분석 (복귀에도 사후 분석 근거를 남긴다)
set +u
NAME=${1:-ret}; X=${2:-0.0}; Y=${3:-0.0}; YAW=${4:-0}
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
BAG=/tmp/bag_$NAME; rm -rf $BAG
setsid nohup ros2 bag record -o $BAG /tf /tf_static /map /scan /plan /local_plan /local_costmap/costmap /global_costmap/costmap /odometry/filtered /cmd_vel /cmd_vel_nav /rover/stuck > /tmp/bag_$NAME.log 2>&1 &
sleep 4
MARK=$(wc -l < /tmp/nav2.log)
python3 /tmp/job207_return.py $X $Y $YAW 150 2>&1 | grep -aE "현재 map|결과|최종" | sed 's/^/  /'
sleep 2; pkill -INT -f "ros2 bag record"; sleep 3
tail -n +$((MARK+1)) /tmp/nav2.log > /tmp/ret.log
for pat in "detected collision" "clear except" "clear entirely" "Running backup" "backup completed" "backup failed" "Running wait" "STUCK" "Goal succeeded" "Goal failed"; do
  c=$(grep -ac "$pat" /tmp/ret.log); [ "$c" != "0" ] && printf "  %-20s %s건\n" "$pat" "$c"
done
echo "  bag: $(du -sh $BAG 2>/dev/null | cut -f1)"
