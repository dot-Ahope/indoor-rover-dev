#!/bin/bash
# 11-04 §17: launch 기본값 변경분을 Jetson src 로(백업 /tmp/deploy_backup_1104b) + --show-args 로 기본값 확인. 빌드 안 함 · 아무것도 띄우지 않음 · 로버 안 움직임.
set -e; S=~/ros2_ws/src; B=/tmp/deploy_backup_1104b; mkdir -p $B; rm -rf /tmp/dep1104b; mkdir /tmp/dep1104b; tar xzf /tmp/dep1104b.tgz -C /tmp/dep1104b
for f in rover_navigation/launch/navigation.launch.py rover_navigation/config/nav2_params.yaml rover_bringup/launch/ekf.launch.py rover_bringup/launch/camera.launch.py; do mkdir -p $B/$(dirname $f); cp -p $S/$f $B/$f; cp /tmp/dep1104b/$f $S/$f; done
cp /tmp/dep1104b/tools/prep_patrol.sh /tmp/prep_patrol.sh
echo "== 설치본 링크"; for f in rover_navigation/launch/navigation.launch.py rover_navigation/config/nav2_params.yaml rover_bringup/launch/ekf.launch.py rover_bringup/launch/camera.launch.py; do i=$(find ~/ros2_ws/install -path "*$(basename $f)" | head -1); [ -L "$i" ] && echo "링크 $(basename $f)" || echo "일반 $(basename $f) $i"; done
set +e; source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
sa(){ ros2 launch $1 $2 --show-args 2>&1 | awk -v pat="$3" '/^ +'"'"'/{n=$0} /default:/{ if (n ~ pat) {gsub(/^ +/,"",n); gsub(/^ +/,"",$0); print n, $0} }'; }
echo "== navigation"; sa rover_navigation navigation.launch.py "replan_hz|mppi_viz|global_camera|stuck_shadow|camera_layer|'planner'|pad_relief"
echo "== ekf"; sa rover_bringup ekf.launch.py "'vslam'|dds_shm|'rf2o'"
echo "== camera"; sa rover_bringup camera.launch.py "emitter_off|dds_shm|depth_preset|emitter_flash"
