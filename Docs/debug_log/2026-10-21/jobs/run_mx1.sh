#!/bin/bash
# 10-21 §19 mx1 — 로버 안 움직임. 주행 스택 내리고(base 유지) 시험 컨테이너 isaac_rs_test 에서 카메라만 띄워
#   번갈이 중 수동 노출 · 게인 단계 시험(P60 → P30). 끝나면 카메라 종료(스택 복귀는 prep 별도).
#   launch · 분석 파일은 PC 가 base64 로 붙여 넣는다(@@LAUNCH@@ · @@ANAL@@).
set +u
N=isaac_rs_test; OLD=isaac_ros_dev-aarch64-container
echo "@@LAUNCH@@" | base64 -d > /tmp/mx_cam.launch.py; echo "@@ANAL@@" | base64 -d > /tmp/anal_mx1.py
PATS="nvblox_up.sh nvblox_node depth_relay.py navigation.launch slam.launch sensors.launch ekf.launch navigation_launch controller_server planner_server bt_navigator behavior_server velocity_smoother smoother_server waypoint_follower lifecycle_manager stuck_monitor nav_guard slam_toolbox ekf_node sensor_conditioner scan_deskew rplidar realsense2_camera foxglove_bridge emitter_splitter cuvslam_up.sh vslam_twist rf2o"
for p in $PATS; do pkill -TERM -f "$p" 2>/dev/null; done; sleep 5; for p in $PATS; do pkill -9 -f "$p" 2>/dev/null; done; sleep 1
docker exec $OLD bash -c "pkill -INT -f 'nvblox_node|cuvslam_[c]ontainer|cuvslam_[a]ctive'; sleep 2; pkill -9 -f 'nvblox_node|cuvslam_[c]ontainer|cuvslam_[a]ctive'" 2>/dev/null
echo "== 스택 내림: 호스트 카메라 $(pgrep -fc realsense2_camera_node) · base $(systemctl --user is-active rover-base)"
docker start $N >/dev/null 2>&1; sleep 2
SRC='source /opt/ros/humble/setup.bash'
for F in 60 30; do
  : > /tmp/mx_cam_$F.log
  docker exec -d -u admin $N bash -c "$SRC; export MX_FPS=$F; exec ros2 launch /tmp/mx_cam.launch.py > /tmp/mx_cam_$F.log 2>&1"
  sleep 18
  echo "======== P$F 기동"; grep -aoE "Device FW version: [0-9.]+|RealSense ROS v[0-9.]+|Open profile: stream_type: (Depth|Infra)[^,]*, Format: [A-Z0-9]+, Width: [0-9]+, Height: [0-9]+, FPS: [0-9]+|Failed to set value to sensor: [^ ]+ = [0-9]+" /tmp/mx_cam_$F.log | sort -u
  docker exec -u admin $N bash -c "$SRC; python3 -u /tmp/anal_mx1.py $F"
  echo "  드라이버 오류(시험 중):"; grep -aE "failed|Failed|ERROR" /tmp/mx_cam_$F.log | sed 's/\x1b\[[0-9;]*m//g' | grep -v "re-enable" | cut -c1-200 | sort | uniq -c | sort -rn | head -8
  pkill -INT -f 'mx_cam.launch.py|__node:=mx_container'; sleep 3; pkill -9 -f 'mx_cam.launch.py|__node:=mx_container'; sleep 3
done
echo "== 끝: mx_container 남은 $(pgrep -fc '__node:=mx_[c]ontainer') (스택은 prep 으로 복귀 필요)"
