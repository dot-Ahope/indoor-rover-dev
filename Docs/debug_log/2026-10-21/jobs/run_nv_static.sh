#!/bin/bash
# 10-21 §18 3번 정지 시험 nv1 — 로버 안 움직임. 주행 스택을 내리고(base 유지) 새 이미지 컨테이너 isaac_rs_test 안에서
#   NVIDIA 구성(드라이버 4.51.1-isaac + realsense_splitter + cuVSLAM, 한 프로세스)을 띄워 anal_nv_static.py 로 잰다.
#   단계: F = 번갈이(NVIDIA) 60 s 측정 → O = 같은 드라이버 프로젝터 상시 끔 대조 30 s. 끝나면 시험 컨테이너 프로세스 정리(스택 복귀는 prep 별도).
#   launch · 분석 파일은 PC 가 base64 로 붙여 넣는다(@@LAUNCH@@ · @@ANAL@@).
set +u
N=isaac_rs_test; OLD=isaac_ros_dev-aarch64-container
echo "@@LAUNCH@@" | base64 -d > /tmp/nv_static.launch.py; echo "@@ANAL@@" | base64 -d > /tmp/anal_nv_static.py
PATS="nvblox_up.sh nvblox_node depth_relay.py navigation.launch slam.launch sensors.launch ekf.launch navigation_launch controller_server planner_server bt_navigator behavior_server velocity_smoother smoother_server waypoint_follower lifecycle_manager stuck_monitor nav_guard slam_toolbox ekf_node sensor_conditioner scan_deskew rplidar realsense2_camera foxglove_bridge emitter_splitter cuvslam_up.sh vslam_twist rf2o"
for p in $PATS; do pkill -TERM -f "$p" 2>/dev/null; done; sleep 5; for p in $PATS; do pkill -9 -f "$p" 2>/dev/null; done; sleep 1
docker exec $OLD bash -c "pkill -INT -f 'nvblox_node|cuvslam_[c]ontainer|cuvslam_[a]ctive'; sleep 2; pkill -9 -f 'nvblox_node|cuvslam_[c]ontainer|cuvslam_[a]ctive'" 2>/dev/null
echo "== 정리 뒤 남은 스택 프로세스: $(for p in $PATS; do pgrep -f "$p" | wc -l; done | awk '{s+=$1} END {print s}') · 옛 컨테이너 nvblox/cuVSLAM $(docker exec $OLD bash -c "pgrep -fc 'nvblox_node|cuvslam_[c]ontainer' || true") · base $(systemctl --user is-active rover-base)"
docker start $N >/dev/null 2>&1; sleep 2
cpu_pct() { local a b; a=$(head -1 /proc/stat); sleep 10; b=$(head -1 /proc/stat); echo "$a $b" | awk '{ta=0; tb=0; for (i=2;i<=9;i++) ta+=$i; for (i=13;i<=20;i++) tb+=$i; printf "%.1f\n", 100*(1-(($16+$17)-($5+$6))/(tb-ta))}'; }
run_phase() {   # $1 = flash|off, $2 = 측정 s
  : > /tmp/nv_static_$1.log
  docker exec -d -u admin $N bash -c "source /opt/ros/humble/setup.bash; source /workspaces/isaac_ros-dev/install_rs/setup.bash; export NV_MODE=$1; exec ros2 launch /tmp/nv_static.launch.py > /tmp/nv_static_$1.log 2>&1"
  sleep 22
  echo "== [$1] 기동 로그"; grep -aoE "Device FW version: [0-9.]+|Built with LibRealSense v[0-9.]+|RealSense ROS v[0-9.]+|RealSense Node Is Up!|Failed to set value to sensor: [^ ]+ = [0-9]+|hwmon command [^(]*|Loaded node [^ ]*|Failed to load node [^ ]*|Open profile: [^,]*, [^,]*, Format: [A-Z0-9]+, FPS: [0-9]+" /tmp/nv_static_$1.log | sort -u | head -16
  grep -aiE "error|fail|warn" /tmp/nv_static_$1.log | grep -v -i "hdr" | sort | uniq -c | sort -rn | head -6
  P=$(pgrep -f '__node:=nv_static_container' | head -1); echo "  컨테이너 프로세스 pid $P"
  echo -n "  전체 CPU(10 s, 코어 6 = 100 %): "; cpu_pct
  echo -n "  nv_static 프로세스 CPU(top 5 회, 코어 1 = 100): "; for i in 1 2 3 4 5; do top -b -n1 -p $P | awk -v p=$P '$1==p {print $9}'; sleep 1; done | awk '{s+=$1; n++} END {printf "%.1f\n", s/n}'
  docker exec -u admin $N bash -c "source /opt/ros/humble/setup.bash; source /workspaces/isaac_ros-dev/install_rs/setup.bash; python3 -u /tmp/anal_nv_static.py $2 $1"
  echo "  cuVSLAM 경고 수: $(grep -ac -iE 'jitter|delta between current and previous frame|Visual tracking is lost' /tmp/nv_static_$1.log)"
  docker exec $N bash -c "pkill -INT -f 'nv_static.launch.py|__node:=nv_static_container'; sleep 3; pkill -9 -f 'nv_static.launch.py|__node:=nv_static_container'" 2>/dev/null; sleep 3
  echo "  [$1] 정리: 남은 $(pgrep -fc '__node:=nv_static_container')"
}
run_phase flash 60
run_phase off 30
echo "== 끝 (스택은 prep 으로 복귀 필요, 시험 컨테이너 $N 는 떠 있음)"
