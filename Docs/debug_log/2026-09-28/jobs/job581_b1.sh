#!/bin/bash
# B1 오프라인 검증 래퍼(Jetson, 2026-09-28): 도메인 42 에서 slam_toolbox(use_sim_time) 를 설정별로 띄우고 job580 으로 bag 재생.
#   라이브 스택(도메인 0)과 섞이지 않는다. 인자: BAG VARIANT(base|a)
#   base = 현재 slam.yaml 그대로 / a = minimum_travel_distance 0.0 + minimum_time_interval 0.5
set +u
BAG=$1; V=$2
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml
export ROS_DOMAIN_ID=42
# 09-28: 앞 실행의 노드가 남으면 같은 도메인에 SLAM 이 둘 → 시작 전·끝에 도메인 42 재생용 노드를 모두 정리
pkill -9 -f "async_slam_toolbox_node.*use_sim_time:=true" 2>/dev/null; sleep 1
Y=$(ros2 pkg prefix rover_bringup)/share/rover_bringup/config/slam.yaml
EXTRA=""; [ "$V" = a ] && EXTRA="-p minimum_travel_distance:=0.0 -p minimum_time_interval:=0.5"
setsid ros2 run slam_toolbox async_slam_toolbox_node --ros-args --params-file $Y -p use_sim_time:=true $EXTRA > /tmp/b1_slam_$V.log 2>&1 &
for i in $(seq 1 15); do ros2 param get /slam_toolbox use_sim_time >/dev/null 2>&1 && break; sleep 1; done
SP=$(pgrep -f "lib/slam_toolbox/async_slam_toolbox_node.*use_sim_time:=true" | head -1)
C0=$(awk '{print $14+$15}' /proc/$SP/stat); T0=$(date +%s.%N)
echo "== $BAG / 설정 $V (slam pid $SP, 매개변수 확인: $(ros2 param get /slam_toolbox minimum_travel_distance 2>/dev/null | tail -1) / $(ros2 param get /slam_toolbox minimum_time_interval 2>/dev/null | tail -1))"
python3 /tmp/job580_slamreplay.py $BAG 2>&1 | grep -av "^\["
C1=$(awk '{print $14+$15}' /proc/$SP/stat); T1=$(date +%s.%N)
awk -v c0=$C0 -v c1=$C1 -v t0=$T0 -v t1=$T1 'BEGIN{printf "  slam CPU 평균 %.1f %% (재생 %.0f s)\n", (c1-c0)/100/(t1-t0)*100, t1-t0}'
pkill -INT -f "async_slam_toolbox_node.*use_sim_time:=true" 2>/dev/null; sleep 2; pkill -9 -f "async_slam_toolbox_node.*use_sim_time:=true" 2>/dev/null
echo "  남은 재생용 slam: $(pgrep -fc "async_slam_toolbox_node.*use_sim_time:=true")"
