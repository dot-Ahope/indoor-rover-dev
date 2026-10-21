#!/bin/bash
# 10-21 §19.2 mx2 — 로버 안 움직임. 주행 스택 내리고(base 유지) 시험 컨테이너에서 카메라만, P30 번갈이.
#   설정마다 다시 기동(기동 파라미터로 노출 · 게인 고정) → anal_mx1.py 30 <이름> 으로 6 s 측정 + 모드별 IR · 깊이 그림 저장.
#   순서: 자동(기준) → A 24000×248 → B 28000×248 → C 32000×248 → D 32000×128 → 대조(상시 끔 + 자동). 그림은 끝에 base64 로 PC 에 보냄.
#   launch · 분석 파일은 PC 가 base64 로 붙여 넣는다(@@LAUNCH@@ · @@ANAL@@).
set +u
N=isaac_rs_test; OLD=isaac_ros_dev-aarch64-container
echo "@@LAUNCH@@" | base64 -d > /tmp/mx_cam.launch.py; echo "@@ANAL@@" | base64 -d > /tmp/anal_mx1.py
PATS="nvblox_up.sh nvblox_node depth_relay.py navigation.launch slam.launch sensors.launch ekf.launch navigation_launch controller_server planner_server bt_navigator behavior_server velocity_smoother smoother_server waypoint_follower lifecycle_manager stuck_monitor nav_guard slam_toolbox ekf_node sensor_conditioner scan_deskew rplidar realsense2_camera foxglove_bridge emitter_splitter cuvslam_up.sh vslam_twist rf2o"
for p in $PATS; do pkill -TERM -f "$p" 2>/dev/null; done; sleep 3; for p in $PATS; do pkill -9 -f "$p" 2>/dev/null; done; sleep 1
docker exec $OLD bash -c "pkill -9 -f 'nvblox_node|cuvslam_[c]ontainer|cuvslam_[a]ctive'" 2>/dev/null
echo "== 스택 내림: 호스트 카메라 $(pgrep -fc realsense2_camera_node) · base $(systemctl --user is-active rover-base)"
docker start $N >/dev/null 2>&1; sleep 2
rm -rf /tmp/mx_img
SRC='source /opt/ros/humble/setup.bash'
run() {   # $1 이름, $2 환경 변수들
  : > /tmp/mx2_$1.log
  docker exec -d -u admin $N bash -c "$SRC; export MX_FPS=30 $2; exec ros2 launch /tmp/mx_cam.launch.py > /tmp/mx2_$1.log 2>&1"
  sleep 16
  echo "======== $1 ($2)"; grep -aoE "Open profile: stream_type: (Depth|Infra)\(1?0?\)[^,]*, Format: [A-Z0-9]+, Width: [0-9]+, Height: [0-9]+, FPS: [0-9]+" /tmp/mx2_$1.log | sort -u | head -2
  docker exec -u admin $N bash -c "$SRC; python3 -u /tmp/anal_mx1.py 30 $1" | grep -v "^프로필"
  echo "  드라이버 오류: $(grep -acE 'failed|Failed|ERROR' /tmp/mx2_$1.log)건 — $(grep -aoE 'option:[A-Za-z ]+, value:[0-9]+ \) [A-Za-z]+|Failed to set value to sensor: [^ ]+ = [0-9]+' /tmp/mx2_$1.log | sort | uniq -c | tr '\n' ';')"
  pkill -INT -f 'mx_cam.launch.py|__node:=mx_container'; sleep 3; pkill -9 -f 'mx_cam.launch.py|__node:=mx_container'; sleep 3
}
run Auto ""
run A24k248 "MX_EXP=24000 MX_GAIN=248"
run B28k248 "MX_EXP=28000 MX_GAIN=248"
run C32k248 "MX_EXP=32000 MX_GAIN=248"
run D32k128 "MX_EXP=32000 MX_GAIN=128"
run Ctl "MX_OFF=1"
echo "== 끝: mx_container 남은 $(pgrep -fc '__node:=mx_[c]ontainer') (스택은 prep 으로 복귀 필요)"
ls /tmp/mx_img | tr '\n' ' '; echo
echo "@@IMG_BEGIN@@"; tar -C /tmp -czf - mx_img | base64 -w0; echo; echo "@@IMG_END@@"
