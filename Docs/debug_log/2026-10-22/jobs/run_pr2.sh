#!/bin/bash
# 10-22 §14 pr2 — 로버 안 움직임. 깊이 프리셋 0 · 3 · 5(Medium Density) 정지 비교(10-21 pr1 과 같은 도구 anal_pr1.py, 같은 자리 · 같은 측정 20 s).
#   (2) 주행 스택 내림(base · robot_state_publisher 유지) (3) 운용 카메라(emitter_off)를 프리셋 0 → 3 → 5 로 기동해 anal_pr1.py 20 s
#   (4) 그림 파일은 끝에 base64 로 PC 에. 스택 복귀는 prep 별도. @@ANAL@@ 는 PC 가 채움.
set +u
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "@@ANAL@@" | base64 -d > /tmp/anal_pr1.py
PATS="nvblox_up.sh nvblox_node depth_relay.py navigation.launch slam.launch sensors.launch ekf.launch navigation_launch controller_server planner_server bt_navigator behavior_server velocity_smoother smoother_server waypoint_follower lifecycle_manager stuck_monitor nav_guard slam_toolbox ekf_node sensor_conditioner scan_deskew rplidar realsense2_camera foxglove_bridge emitter_splitter cuvslam_up.sh vslam_twist rf2o"
for p in $PATS; do pkill -TERM -f "$p" 2>/dev/null; done; sleep 4; for p in $PATS; do pkill -9 -f "$p" 2>/dev/null; done; sleep 1
docker exec isaac_ros_dev-aarch64-container bash -c "pkill -9 -f 'nvblox_[n]ode|cuvslam_[c]ontainer|cuvslam_[a]ctive'" 2>/dev/null
echo "== 스택 내림: 카메라 $(pgrep -fc realsense2_camera) · base $(systemctl --user is-active rover-base) · RSP $(pgrep -fc robot_state_publisher)"
rm -f /tmp/pr1_*
for ph in P0c:0 P3b:3 P5:5; do
  T=${ph%%:*}; PR=${ph##*:}
  setsid nohup ros2 launch rover_bringup camera.launch.py emitter_off:=true depth_preset:=$PR > /tmp/pr1_cam_$T.log 2>&1 < /dev/null &
  sleep 15
  echo "======== $T (depth_preset:=$PR) — $(ros2 param get /camera/camera depth_module.visual_preset 2>&1) · $(grep -aoE 'Open profile: stream_type: Depth[^,]*, Format: [A-Z0-9]+, Width: [0-9]+, Height: [0-9]+, FPS: [0-9]+' /tmp/pr1_cam_$T.log | head -1)"
  echo "  드라이버 경고: $(grep -aciE 'failed|error' /tmp/pr1_cam_$T.log)건 $(grep -aoiE '(Failed to set|Set parameter)[^.]{0,90}(preset|Preset)[^.]{0,40}' /tmp/pr1_cam_$T.log | head -2 | tr '\n' ';')"
  python3 -u /tmp/anal_pr1.py 20 $T 2>&1 | grep -v "^\[INFO\]"
  pkill -INT -f 'camera.launch.py'; sleep 3; pkill -9 -f 'realsense2_camera|camera.launch.py|depth_relay' 2>/dev/null; sleep 3
done
echo "== 끝: 카메라 남은 $(pgrep -fc realsense2_camera) (스택은 prep 으로 복귀 필요)"
echo "@@IMG_BEGIN@@"; tar -C /tmp -czf - $(cd /tmp; ls pr1_*.npz pr1_*.png 2>/dev/null) | base64 -w0; echo; echo "@@IMG_END@@"
