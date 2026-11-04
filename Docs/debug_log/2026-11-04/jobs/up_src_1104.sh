#!/bin/bash
# 11-04 §10: 저장소 판(주석 정정 · pad_relief 기본 off · place_server RCLError · places.yaml 주석)을 Jetson src 로. 원본 백업 · 전후 md5 · 설치본 링크 여부. 빌드 안 함 · 로버 안 움직임 · sudo 없음.
set -e; S=~/ros2_ws/src; B=/tmp/deploy_backup_1104; mkdir -p $B; rm -rf /tmp/dep1104; mkdir /tmp/dep1104; tar xzf /tmp/dep1104.tgz -C /tmp/dep1104
for f in rover_navigation/config/nav2_params.yaml rover_navigation/config/nvblox_local.yaml rover_navigation/config/nav_to_pose_no_spin.xml rover_navigation/config/places.yaml rover_navigation/launch/navigation.launch.py rover_navigation/scripts/place_server.py rover_navigation/src/path_blocked_ahead_condition.cpp rover_bringup/launch/camera.launch.py rover_bringup/config/fastdds_udp_only.xml rover_bringup/scripts/pad_relief.py rover_bringup/scripts/rf2o_gate.py; do
  old=$(tr -d '\r' < $S/$f | md5sum | cut -c1-8); mkdir -p $B/$(dirname $f); cp -p $S/$f $B/$f
  cp /tmp/dep1104/$f $S/$f; new=$(md5sum < $S/$f | cut -c1-8)
  i=$(find ~/ros2_ws/install -path "*$(basename $f)" 2>/dev/null | head -1); lk=$([ -n "$i" ] && { [ -L "$i" ] && echo 링크 || echo 일반파일; } || echo 설치본없음)
  echo "$old → $new  $f  (설치본 $lk)"
done
cp /tmp/dep1104/prep_fast.sh /tmp/prep_fast.sh; echo "/tmp/prep_fast.sh cuvslam 포함 줄 $(grep -c 'cuvslam.log /tmp/nvblox_node.log' /tmp/prep_fast.sh)"
