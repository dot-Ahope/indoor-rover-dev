#!/bin/bash
# 검증 주행 — BT 수정(ClearCostmapExceptRegion) + 감쇠 복원(로컬 30초 선형) 상태.
# bag 기록 + 주행 + nav2 로그 분석을 한 번에.
export FASTRTPS_DEFAULT_PROFILES_FILE=$HOME/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
NAME=${1:-job231}; D=${2:-1.60}; TMO=${3:-90}
# 2026-09-18 §17: 기본 목록 + /plan_smoothed·/unsmoothed_plan(스무더 결과, 09-18 §15 에서 없어서 재현해야 했음) + BAG_EXTRA(단계별 추가 토픽, 러너 환경변수).
#   기록한 목록·실행 중 파라미터·배포 파일 해시는 job453 이 bag 폴더에 남긴다(run_meta.txt, params.txt).
TOPICS="/tf /tf_static /map /scan /plan /plan_smoothed /unsmoothed_plan /local_plan /transformed_global_plan /local_costmap/costmap /global_costmap/costmap /odometry/filtered /wheel_odom /cmd_vel /rover/status /battery /rover/stuck ${BAG_EXTRA:-}"
export TOPICS   # 09-21 cc1: 메타(job453, 파라미터 조회 노드·topic list 등 DDS 참여자 생성/소멸)를 주행 직전에 돌렸더니 루프 미달 18·EKF 위반 61 — 디스커버리 부하 의심 → bag 종료 뒤로 옮김
BAG=/tmp/bag_$NAME
rm -rf $BAG
setsid nohup ros2 bag record -o $BAG $TOPICS > /tmp/bag_$NAME.log 2>&1 &
# 09-17 mp7: 주행 중 CPU 굶주림(SLAM map->odom 5 s 끊김)의 범인을 가리기 위해 2 s 마다 프로세스별 CPU 기록
setsid nohup top -b -d 2 -w 180 -o %CPU > /tmp/top_$NAME.log 2>&1 &
# 09-21 S5 기준선: GPU·전력·온도(tegrastats, 1 s)와 노드별 RSS(ps, DDS 무관) — 코스트맵 주기는 bag 에서 사후 계산(주행 전 ros2 topic hz 금지 규칙)
setsid nohup tegrastats --interval 1000 > /tmp/tegra_$NAME.log 2>&1 &
ps -eo pid,rss,pcpu,comm,args --sort=-rss | grep -E "controller_server|planner_server|bt_navigator|smoother_server|behavior_server|velocity_smoother|slam_toolbox|ekf_node|realsense2|rplidar|depth_relay|sensor_conditioner|stuck_monitor|micro_ros|robot_state_pub|lifecycle" | grep -v grep | cut -c1-140 > /tmp/rss_$NAME.txt
sleep 4
MARK=$(wc -l < /tmp/nav2.log 2>/dev/null || echo 0)
echo "=== 주행 (bag $(pgrep -fc 'ros2 bag record')개, nav2.log $MARK 줄부터) ==="
python3 /tmp/job125_avoid3.py $D $TMO $NAME 2>&1 | tail -40
sleep 2
pkill -INT -f "ros2 bag record" 2>/dev/null
pkill -f "top -b -d 2 -w 180" 2>/dev/null
pkill -f "tegrastats --interval 1000" 2>/dev/null; echo "--- after ---" >> /tmp/rss_$NAME.txt; ps -eo pid,rss,pcpu,comm,args --sort=-rss | grep -E "controller_server|planner_server|bt_navigator|slam_toolbox|ekf_node|realsense2|depth_relay|sensor_conditioner" | grep -v grep | cut -c1-140 >> /tmp/rss_$NAME.txt; free -m | head -2 >> /tmp/rss_$NAME.txt
for i in $(seq 1 10); do [ "$(pgrep -fc 'ros2 bag record' 2>/dev/null | head -1)" = "0" ] && break; sleep 1; done
sync
bash /tmp/job453_runmeta.sh $NAME $D $TMO   # 09-21: 주행 뒤에 스냅샷(파라미터는 주행 중 안 바뀌므로 재현성 동일)
[ -d /tmp/meta_$NAME ] && mv /tmp/meta_$NAME/* $BAG/ 2>/dev/null && rmdir /tmp/meta_$NAME   # 09-18 §17: 메타를 bag 폴더에(회수 tgz 에 포함)
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
