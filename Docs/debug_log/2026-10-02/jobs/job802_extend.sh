#!/bin/bash
# 10-02 §1: office_v2 이어 그리기(루프 클로저 끔)로 f2a12 bag +CUT 초까지 재생 → 후보 포즈 그래프·격자. 도메인 42·sim time.
#   job719(10-01) 일반화: 기준 지도·bag·출력 이름을 인자로. 격자는 job722 방식(벽시계로 그래프만 불러 map_saver_cli).
set +u
BAG=${BAG:-/home/jetson/bags/bag_f2a12}; CUT=${1:-276}; BASE=${BASE:-office_v2}; D=/home/jetson/maps/office; N=${N:-cand_1002_f2a12_c${CUT}_nolc}; OUT=$D/$N
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash; source ~/slam_ws/install/setup.bash
export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml
export ROS_DOMAIN_ID=42
[ -e $OUT.posegraph ] && { echo "이미 있음: $OUT"; exit 1; }
echo "== 기준 $BASE | bag $BAG (+$CUT s 까지) | 출력 $N | load $(cut -d' ' -f1-3 /proc/loadavg)"
pkill -9 -f "async_slam_toolbox_node.*use_sim_time:=true" 2>/dev/null; sleep 1
Y=$(ros2 pkg prefix rover_bringup)/share/rover_bringup/config/slam.yaml
echo "  slam 실행 파일: $(readlink -f $(ros2 pkg prefix slam_toolbox)/lib/slam_toolbox/async_slam_toolbox_node) | 루프 창: $(grep -aoE 'loop_search_space_dimension: [0-9.]+' $Y)"
setsid ros2 run slam_toolbox async_slam_toolbox_node --ros-args --params-file $Y -p use_sim_time:=true \
  -p map_file_name:=$D/$BASE -p "map_start_pose:=[0.0, 0.0, 0.0]" -p map_start_at_dock:=false -p do_loop_closing:=false > /tmp/ext_slam.log 2>&1 &
for i in $(seq 1 30); do ros2 param get /slam_toolbox use_sim_time >/dev/null 2>&1 && break; sleep 1; done
sleep 5; echo "  do_loop_closing: $(ros2 param get /slam_toolbox do_loop_closing 2>&1 | tail -1)"
python3 -u /tmp/job719_cutreplay.py $BAG $CUT $OUT 2>&1 | grep -av --line-buffered "^\["
echo "== Ceres(루프 클로저) 흔적: $(grep -ac preprocessor.cc /tmp/ext_slam.log)건"
pkill -INT -f "async_slam_toolbox_node.*use_sim_time:=true"; sleep 2; pkill -9 -f "async_slam_toolbox_node.*use_sim_time:=true" 2>/dev/null
ls -la $OUT.* 2>&1
if [ ! -s $OUT.pgm ]; then
  echo "== 격자 생성(job722 방식)"
  setsid ros2 run slam_toolbox async_slam_toolbox_node --ros-args --params-file $Y -p map_file_name:=$OUT -p "map_start_pose:=[0.0, 0.0, 0.0]" -p map_start_at_dock:=false > /tmp/ext_grid.log 2>&1 &
  for i in $(seq 1 40); do timeout 3 ros2 topic echo --once /map_metadata >/dev/null 2>&1 && break; sleep 2; done
  timeout 40 ros2 run nav2_map_server map_saver_cli -f $OUT --ros-args -p map_subscribe_transient_local:=true 2>&1 | grep -aiE "saved|error|fail" | head -3
  pkill -INT -f "async_slam_toolbox_node.*map_file_name:=$OUT"; sleep 2; pkill -9 -f "async_slam_toolbox_node.*map_file_name:=$OUT" 2>/dev/null
fi
ls -la $OUT.*; cat $OUT.yaml
