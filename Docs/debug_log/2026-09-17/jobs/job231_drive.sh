#!/bin/bash
# 검증 주행 — BT 수정(ClearCostmapExceptRegion) + 감쇠 복원(로컬 30초 선형) 상태.
# bag 기록 + 주행 + nav2 로그 분석을 한 번에.
export FASTRTPS_DEFAULT_PROFILES_FILE=$HOME/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
NAME=${1:-job231}; D=${2:-1.60}; TMO=${3:-90}
TOPICS="/tf /tf_static /map /scan /plan /local_plan /transformed_global_plan \
/local_costmap/costmap /global_costmap/costmap \
/odometry/filtered /wheel_odom /cmd_vel /rover/status /battery /rover/stuck"
BAG=/tmp/bag_$NAME
rm -rf $BAG
setsid nohup ros2 bag record -o $BAG $TOPICS > /tmp/bag_$NAME.log 2>&1 &
# 09-17 mp7: 주행 중 CPU 굶주림(SLAM map->odom 5 s 끊김)의 범인을 가리기 위해 2 s 마다 프로세스별 CPU 기록
setsid nohup top -b -d 2 -w 180 -o %CPU > /tmp/top_$NAME.log 2>&1 &
sleep 4
MARK=$(wc -l < /tmp/nav2.log 2>/dev/null || echo 0)
echo "=== 주행 (bag $(pgrep -fc 'ros2 bag record')개, nav2.log $MARK 줄부터) ==="
python3 /tmp/job125_avoid3.py $D $TMO $NAME 2>&1 | tail -40
sleep 2
pkill -INT -f "ros2 bag record" 2>/dev/null
pkill -f "top -b -d 2 -w 180" 2>/dev/null
for i in $(seq 1 10); do [ "$(pgrep -fc 'ros2 bag record' 2>/dev/null | head -1)" = "0" ] && break; sleep 1; done
sync
echo
echo "=== nav2.log 신규분 ==="
tail -n +$((MARK+1)) /tmp/nav2.log > /tmp/nav2_new.log
echo "  신규 $(wc -l < /tmp/nav2_new.log) 줄"
for pat in "detected collision" "clear except" "clear entirely" "backup failed" "Goal succeeded" "aborted"; do
  c=$(grep -ac "$pat" /tmp/nav2_new.log 2>/dev/null)
  printf "  %-20s %s건\n" "$pat" "$c"
done
grep -aE "detected collision|clear except|clear entirely|backup failed" /tmp/nav2_new.log | head -12 | sed 's/^/  /'
echo "  bag: $(du -sh $BAG 2>/dev/null | cut -f1)"
echo "  EKF 위반 $(grep -ac 'Failed to meet update rate' /tmp/sensors.log)회 | slam 폐기 $(grep -ac 'Message Filter dropping' /tmp/slam.log)회 | load $(cut -d' ' -f1-3 /proc/loadavg)"
