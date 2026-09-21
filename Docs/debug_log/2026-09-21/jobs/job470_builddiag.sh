#!/bin/bash
export TERM=xterm
cd ~/workspaces/isaac_ros-dev/src/isaac_ros_common/scripts || exit 1
echo "== 전경 시험 실행 (60 s 제한, TERM=xterm)"; timeout 60 bash -x build_image_layers.sh --image_key aarch64.ros2_humble --image_name isaac_ros_dev-aarch64 2>&1 | grep -av '^+ \(print_\|echo\|local\)' | head -40 | cut -c1-200
echo "== rc=$? | docker images: $(docker images --format '{{.Repository}}:{{.Tag}}' | grep -cE 'isaac|nvcr')"
