#!/bin/bash
# (10-19 §23) 오프라인 cuVSLAM 켬/끔 비교 — 실시간 스택 내림(base 유지, 로버 정지) → 입력 bag 만들기(호스트) → 컨테이너에서 IMU 융합 켬 · 끔 두 판.
#   준비물은 /tmp 에 올려 둔 mk_vslam_bag.py · vslam_offline.launch.py · vslam_run_in.sh · export_vslam.py
set +u
# 10-19 §25: 인자 [이름=f2y1] [all_off] — 입력 bag 은 bag_<이름>_ir · bag_<이름>, 출력 vslam_<이름>_*.csv
NM=${1:-f2y1}; MODE=${2:-}
PATS="nvblox_up.sh nvblox_node depth_relay.py navigation.launch slam.launch sensors.launch navigation_launch controller_server planner_server bt_navigator behavior_server velocity_smoother smoother_server waypoint_follower lifecycle_manager stuck_monitor nav_guard rf2o slam_toolbox ekf_node sensor_conditioner scan_deskew rplidar realsense2_camera foxglove_bridge"
for p in $PATS; do pkill -TERM -f "$p" 2>/dev/null; done; sleep 5; for p in $PATS; do pkill -9 -f "$p" 2>/dev/null; done
CN=isaac_ros_dev-aarch64-container; docker exec $CN bash -c "pkill -f nvblox_node" 2>/dev/null
echo "== 스택 내림: 남은 $(for p in $PATS; do pgrep -f "$p" | wc -l; done | awk '{s+=$1} END {print s}') · base $(systemctl --user is-active rover-base)"
echo "== 컨테이너 마운트: $(docker inspect $CN --format '{{range .Mounts}}{{.Source}}->{{.Destination}} {{end}}' | tr ' ' '\n' | grep isaac_ros-dev)"
W=/home/jetson/workspaces/isaac_ros-dev/vslam; mkdir -p $W
cp /tmp/vslam_offline.launch.py /tmp/vslam_run_in.sh /tmp/export_vslam.py $W/
if [ ! -f $W/${NM}_split/metadata.yaml ]; then rm -rf $W/${NM}_split; nice -n 5 python3 -u /tmp/mk_vslam_bag.py /home/jetson/bags/bag_${NM}_ir /home/jetson/bags/bag_${NM} $W/${NM}_split $MODE 2>&1 | grep -v INFO; fi
du -sh $W/${NM}_split
echo "== 컨테이너 ros2 bag: $(docker exec $CN bash -lc 'source /opt/ros/humble/setup.bash; ros2 bag --help >/dev/null 2>&1 && echo 있음 || echo 없음')"
for IMU in true false; do
  echo "########## cuVSLAM IMU 융합 $IMU ##########"
  # 10-19 §25: 컨테이너 안 ros2 데몬 등이 출력 파이프를 붙잡아 끝나지 않던 문제(§23 시간 초과) — 파일로 받고 시간 제한
  timeout 900 docker exec -u admin $CN bash /workspaces/isaac_ros-dev/vslam/vslam_run_in.sh $IMU ${NM}_split > $W/run_${NM}_$IMU.out 2>&1 < /dev/null; grep -av "^\[INFO\]" $W/run_${NM}_$IMU.out | tail -8
done
ls -la $W/vslam_${NM}_*.csv
