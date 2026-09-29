#!/bin/bash
# 09-29 §10: 프로젝터 번갈이(emitter_on_off) 경로 준비물 확인 — 컨테이너의 splitter 노드, nvblox 예제의 realsense 설정, 드라이버 파라미터
CN=isaac_ros_dev-aarch64-container
docker exec $CN bash -lc "source /opt/ros/humble/setup.bash; ros2 pkg list | grep -iE 'splitter|realsense'; ls /opt/ros/humble/share/nvblox_examples_bringup/config/sensors/ 2>/dev/null; ls /opt/ros/humble/share/nvblox_examples_bringup/launch/sensors/ 2>/dev/null"
docker exec $CN bash -lc "cat /opt/ros/humble/share/nvblox_examples_bringup/config/sensors/realsense.yaml 2>/dev/null | grep -vE '^\s*#' | head -60"
docker exec $CN bash -lc "grep -hE 'splitter|emitter|plugin|remap|input|output' /opt/ros/humble/share/nvblox_examples_bringup/launch/sensors/realsense.launch.py 2>/dev/null | head -40"
echo "== 호스트 드라이버의 emitter 관련 파라미터"
source /opt/ros/humble/setup.bash; export FASTRTPS_DEFAULT_PROFILES_FILE=/tmp/fastdds_udp_only.xml
timeout 8 ros2 param list /camera/camera 2>/dev/null | grep -iE "emitter|laser|infra_profile|hdr"
