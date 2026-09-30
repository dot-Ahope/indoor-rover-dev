#!/bin/bash
# 09-30 F1: SLAM 지도 저장 — 포즈 그래프(이어 그리기용 .posegraph/.data) + 격자(pgm/yaml, Nav2·편집용). 인자: 이름
set +u; N=${1:?이름}; D=/home/jetson/maps/office; mkdir -p $D
source /opt/ros/humble/setup.bash; export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml
[ -e $D/$N.posegraph ] && { echo "이미 있음: $D/$N — 다른 이름을 쓰세요"; exit 1; }
timeout 60 ros2 service call /slam_toolbox/serialize_map slam_toolbox/srv/SerializePoseGraph "{filename: '$D/$N'}" 2>&1 | tail -1
timeout 60 ros2 service call /slam_toolbox/save_map slam_toolbox/srv/SaveMap "{name: {data: '$D/$N'}}" 2>&1 | tail -1
ls -la $D/$N.* 2>&1
grep -E "resolution|origin" $D/$N.yaml 2>/dev/null
