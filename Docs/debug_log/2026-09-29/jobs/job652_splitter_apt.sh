#!/bin/bash
# 09-29 §10: realsense_splitter 설치 가능 여부, emitter_flashing 예제 설정 원문
CN=isaac_ros_dev-aarch64-container
docker exec $CN bash -lc "source /opt/ros/humble/setup.bash; ros2 pkg prefix realsense_splitter 2>&1 | tail -1; apt-cache policy ros-humble-realsense-splitter 2>/dev/null | head -4"
echo "== realsense_emitter_flashing.yaml"
docker exec $CN bash -lc "grep -vE '^\s*#|^\s*$' /opt/ros/humble/share/nvblox_examples_bringup/config/sensors/realsense_emitter_flashing.yaml"
echo "== realsense_emitter_on.yaml (차이 확인용)"
docker exec $CN bash -lc "diff <(grep -vE '^\s*#|^\s*$' /opt/ros/humble/share/nvblox_examples_bringup/config/sensors/realsense_emitter_on.yaml) <(grep -vE '^\s*#|^\s*$' /opt/ros/humble/share/nvblox_examples_bringup/config/sensors/realsense_emitter_flashing.yaml)"
