#!/bin/bash
# 10-01 §9: 위치 추정 모드 부하 A/B — 도메인 42 에서 localization_slam_toolbox_node(office_v2, sim time)를 변형별로 띄우고 job736 재생.
#   변형: base = 현 slam.yaml(노드 간격 0.05 m·0.03 rad) / t2 = 0.20 m·0.10 rad / t1 = 0.10 m·0.05 rad
#   라이브 스택(도메인 0)은 건드리지 않음 — 다만 CPU 를 나눠 쓰므로 라이브 스택은 미리 정지(STOP_LIVE=1, 기본).
set +u; END=${END:-560}
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash; source ~/slam_ws/install/setup.bash
export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml
if [ "${STOP_LIVE:-1}" = 1 ]; then
  for p in navigation.launch slam.launch localization.launch controller_server planner_server bt_navigator behavior_server velocity_smoother smoother_server waypoint_follower lifecycle_manager slam_toolbox nvblox_up.sh stuck_monitor nav_guard; do pkill -f "$p" 2>/dev/null; done
  docker exec isaac_ros_dev-aarch64-container bash -c "pkill -f nvblox_node" 2>/dev/null; sleep 3
  echo "== 라이브 Nav2·SLAM·nvblox 정지(센서·EKF·에이전트 유지) | load $(cut -d' ' -f1-3 /proc/loadavg)"
fi
export ROS_DOMAIN_ID=42
Y=$(ros2 pkg prefix rover_bringup)/share/rover_bringup/config/slam.yaml
for V in ${@:-base t2}; do   # 인자 = 변형 목록
  pkill -9 -f "slam_toolbox_node.*use_sim_time:=true" 2>/dev/null; sleep 1
  case $V in base) EX="" ;; t2) EX="-p minimum_travel_distance:=0.20 -p minimum_travel_heading:=0.10" ;; t1) EX="-p minimum_travel_distance:=0.10 -p minimum_travel_heading:=0.05" ;; t3) EX="-p minimum_travel_distance:=0.30 -p minimum_travel_heading:=0.15" ;; t2nolc) EX="-p minimum_travel_distance:=0.20 -p minimum_travel_heading:=0.10 -p do_loop_closing:=false" ;; t3m) EX="-p minimum_travel_distance:=0.30 -p minimum_travel_heading:=0.15 -p map_update_interval:=10.0" ;; t2m) EX="-p minimum_travel_distance:=0.20 -p minimum_travel_heading:=0.10 -p map_update_interval:=10.0" ;; esac
  setsid ros2 run slam_toolbox localization_slam_toolbox_node --ros-args --params-file $Y -p use_sim_time:=true -p mode:=localization \
    -p map_file_name:=/home/jetson/maps/office/office_v2 -p "map_start_pose:=[0.0, 0.0, 0.0]" -p map_start_at_dock:=false $EX > /tmp/locrep_$V.log 2>&1 &
  for i in $(seq 1 30); do ros2 param get /slam_toolbox use_sim_time >/dev/null 2>&1 && break; sleep 1; done; sleep 8
  SP=$(pgrep -f "lib/slam_toolbox/localization_slam_toolbox_node.*use_sim_time:=true" | head -1)
  echo; echo "########## 변형 $V: 거리 $(ros2 param get /slam_toolbox minimum_travel_distance 2>/dev/null | grep -oE '[0-9.]+$') · 회전 $(ros2 param get /slam_toolbox minimum_travel_heading 2>/dev/null | grep -oE '[0-9.]+$') · 모드 $(ros2 param get /slam_toolbox mode 2>/dev/null | grep -oE '[a-z]+$') · pid $SP · load $(cut -d' ' -f1-3 /proc/loadavg)"
  SLAM_PID=$SP python3 -u /tmp/job736_locreplay.py /home/jetson/bags/map_0930_1724 $END 2>&1 | grep -av --line-buffered "^\["
  pkill -INT -f "slam_toolbox_node.*use_sim_time:=true"; sleep 2; pkill -9 -f "slam_toolbox_node.*use_sim_time:=true" 2>/dev/null
done
