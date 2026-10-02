#!/bin/bash
# 10-02 §2: 위치 추정 재생 3 조합 — 인자 "지도:탐색창" 목록. 운용과 같은 위치 추정 설정(slam.launch 의 0.30·0.15·갱신 10·tt 0.5).
set +u
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash; source ~/slam_ws/install/setup.bash
export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml
export ROS_DOMAIN_ID=42; D=/home/jetson/maps/office
Y=$(ros2 pkg prefix rover_bringup)/share/rover_bringup/config/slam.yaml
for V in "$@"; do
  MAP=${V%%:*}; WIN=${V##*:}
  pkill -9 -f "slam_toolbox_node.*use_sim_time:=true" 2>/dev/null; sleep 1
  setsid ros2 run slam_toolbox localization_slam_toolbox_node --ros-args --params-file $Y -p use_sim_time:=true -p mode:=localization \
    -p map_file_name:=$D/$MAP -p "map_start_pose:=[0.0, 0.0, 0.0]" -p map_start_at_dock:=false \
    -p minimum_travel_distance:=0.30 -p minimum_travel_heading:=0.15 -p map_update_interval:=10.0 -p transform_timeout:=0.5 \
    -p loop_search_space_dimension:=$WIN > /tmp/locjump_${MAP}_${WIN}.log 2>&1 &
  for i in $(seq 1 40); do ros2 param get /slam_toolbox use_sim_time >/dev/null 2>&1 && break; sleep 1; done; sleep 10
  echo; echo "########## 지도 $MAP · 탐색 창 $(ros2 param get /slam_toolbox loop_search_space_dimension 2>/dev/null | grep -oE '[0-9.]+$') · 모드 $(ros2 param get /slam_toolbox mode 2>/dev/null | grep -oE '[a-z]+$') · load $(cut -d' ' -f1-3 /proc/loadavg)"
  python3 -u /tmp/job803_locjump.py /home/jetson/bags/bag_f2a12 /tmp/locjump_${MAP}_${WIN}.npz 2>&1 | grep -av --line-buffered "^\["
  pkill -INT -f "slam_toolbox_node.*use_sim_time:=true"; sleep 2; pkill -9 -f "slam_toolbox_node.*use_sim_time:=true" 2>/dev/null
done
