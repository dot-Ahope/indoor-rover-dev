#!/bin/bash
# (10-19 §24) IR 노출 · 게인 정지 시험 — 스택 내리고(base 유지) 카메라 단독(번갈이 30, 지금 설정) → chk_ir_exposure.py → 카메라 종료. 로버 안 움직임
set +u
PATS="nvblox_up.sh nvblox_node depth_relay.py navigation.launch slam.launch sensors.launch navigation_launch controller_server planner_server bt_navigator behavior_server velocity_smoother smoother_server waypoint_follower lifecycle_manager stuck_monitor nav_guard rf2o slam_toolbox ekf_node sensor_conditioner scan_deskew rplidar realsense2_camera foxglove_bridge"
for p in $PATS; do pkill -TERM -f "$p" 2>/dev/null; done; sleep 5; for p in $PATS; do pkill -9 -f "$p" 2>/dev/null; done
docker exec isaac_ros_dev-aarch64-container bash -c "pkill -f nvblox_node" 2>/dev/null
echo "== 스택 내림: 남은 $(for p in $PATS; do pgrep -f "$p" | wc -l; done | awk '{s+=$1} END {print s}') · base $(systemctl --user is-active rover-base)"
setsid nohup ros2 run realsense2_camera realsense2_camera_node --ros-args -r __node:=camera -r __ns:=/camera \
  -p enable_depth:=true -p enable_color:=false -p enable_infra1:=true -p enable_infra2:=true \
  -p depth_module.depth_profile:=640x480x30 -p depth_module.infra_profile:=640x480x30 \
  -p depth_module.emitter_enabled:=1 -p depth_module.emitter_on_off:=true -p decimation_filter.enable:=true -p decimation_filter.filter_magnitude:=4 \
  -p enable_gyro:=false -p enable_accel:=false -p initial_reset:=true -p publish_tf:=false > /tmp/irexp_cam.log 2>&1 < /dev/null &
sleep 14
echo "== 카메라: $(grep -aoE 'Open profile: stream_type: (Depth|Infra)[^;]*FPS: [0-9]+' /tmp/irexp_cam.log | sort -u | tr '\n' ';')"
python3 -u /tmp/chk_ir_exposure.py 2>&1 | grep -v "^\[INFO\]"
pkill -INT -f realsense2_camera_node; sleep 3; pkill -9 -f realsense2_camera_node 2>/dev/null
echo "== 끝(스택은 prep 으로 복귀)"
