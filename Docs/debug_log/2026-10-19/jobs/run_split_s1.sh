#!/bin/bash
# (10-19 §15 S1) 분리 노드 정지 시험 — 주행 스택 내리고(base 유지) 카메라를 스택 설정 + 깊이 · IR 640×480×60 + emitter_on_off 로 띄워
#   emitter_splitter_node 를 돌리고 anal_split_s1.py 로 판정 측정. 끝나면 분리 노드 · 카메라 종료(스택은 다음 prep 으로 복귀). 로버 안 움직임
set +u
PATS="nvblox_up.sh nvblox_node depth_relay.py navigation.launch slam.launch sensors.launch navigation_launch controller_server planner_server bt_navigator behavior_server velocity_smoother smoother_server waypoint_follower lifecycle_manager stuck_monitor nav_guard slam_toolbox ekf_node sensor_conditioner scan_deskew rplidar realsense2_camera foxglove_bridge emitter_splitter"
for p in $PATS; do pkill -TERM -f "$p" 2>/dev/null; done; sleep 5; for p in $PATS; do pkill -9 -f "$p" 2>/dev/null; done; sleep 1
CN=isaac_ros_dev-aarch64-container; docker exec $CN bash -c "pkill -f nvblox_node" 2>/dev/null
echo "== 정리 뒤 남은 스택 프로세스: $(for p in $PATS; do pgrep -f "$p" | wc -l; done | awk '{s+=$1} END {print s}') | base: $(systemctl --user is-active rover-base)"
: > /tmp/split_cam.log; : > /tmp/split_node.log
setsid nohup ros2 run realsense2_camera realsense2_camera_node --ros-args -r __node:=camera -r __ns:=/camera \
  -p enable_depth:=true -p enable_color:=true -p enable_infra1:=true -p enable_infra2:=true \
  -p depth_module.depth_profile:=640x480x60 -p depth_module.infra_profile:=640x480x60 -p rgb_camera.color_profile:=640x480x15 \
  -p depth_module.emitter_enabled:=1 -p depth_module.emitter_on_off:=true -p align_depth.enable:=false \
  -p pointcloud.enable:=true -p pointcloud__neon_.enable:=true -p pointcloud__neon_.allow_no_texture_points:=true \
  -p decimation_filter.enable:=true -p decimation_filter.filter_magnitude:=4 \
  -p enable_gyro:=true -p enable_accel:=true -p gyro_fps:=200 -p accel_fps:=100 -p unite_imu_method:=1 \
  -p initial_reset:=true -p publish_tf:=true > /tmp/split_cam.log 2>&1 < /dev/null &
sleep 14
echo "== 카메라: $(grep -aoE 'RealSense Node Is Up!|Open profile: stream_type: [A-Za-z]+[^;]*FPS: [0-9]+' /tmp/split_cam.log | sort -u | tr '\n' ';' | cut -c1-400)"
echo -n "  emitter_on_off: "; timeout 6 ros2 param get /camera/camera depth_module.emitter_on_off 2>&1 | tail -1
setsid nohup ros2 run rover_bringup emitter_splitter_node > /tmp/split_node.log 2>&1 < /dev/null &
sleep 8
echo "== CPU(top 5 회 평균, 코어 1 = 100) — 측정 스크립트 시작 전"
for i in 1 2 3 4 5; do top -b -n1 -w 220 | awk '/realsense2_c|emitter_spli/ {print $NF, $9}'; sleep 1; done | awk '{s[$1]+=$2; n[$1]++} END {for (k in s) printf "  %-22s %.1f %%\n", k, s[k]/n[k]}'
python3 -u /tmp/anal_split_s1.py 20
sleep 12
echo "== 분리 노드 통계(10 s 창)"; grep -a "10 s:" /tmp/split_node.log | sed 's/.*10 s: //' | tail -4
grep -aiE "error|warn" /tmp/split_node.log | head -5
pkill -INT -f emitter_splitter_node; pkill -INT -f realsense2_camera_node; sleep 3; pkill -9 -f emitter_splitter_node; pkill -9 -f realsense2_camera_node 2>/dev/null
echo "== 끝: 카메라 $(pgrep -f realsense2_camera_node | wc -l) · 분리 $(pgrep -f emitter_splitter_node | wc -l) (스택은 prep 으로 복귀 필요)"
