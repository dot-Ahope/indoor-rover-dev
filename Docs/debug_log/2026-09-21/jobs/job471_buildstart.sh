#!/bin/bash
# 09-21: 첫 시도는 TERM 미설정 → print_color 의 tput 이 set -e 아래서 실패해 즉시 종료. TERM=xterm 으로 재시작.
export TERM=xterm; cd ~/workspaces/isaac_ros-dev/src/isaac_ros_common/scripts || exit 1
pkill -f build_image_layers 2>/dev/null; : > /tmp/isaac_build.log
nohup bash build_image_layers.sh --image_key aarch64.ros2_humble --image_name isaac_ros_dev-aarch64 > /tmp/isaac_build.log 2>&1 &
echo "pid $!"; sleep 90; echo "--- 90 s: 로그 $(wc -l < /tmp/isaac_build.log) 줄"; grep -aE "Building|pull|Pulling|Downloading|Extracting|layer|Step|ERROR|error|denied" /tmp/isaac_build.log | tail -8 | cut -c1-160
echo "docker pull 진행: $(pgrep -fa 'docker pull' | cut -c1-120 | head -1) | images: $(docker images --format '{{.Repository}}:{{.Tag}} {{.Size}}' | grep -E 'isaac|nvcr' | tr '\n' ';') | net rx MB $(awk '/wlP1p1s0/{printf "%.0f", $2/1e6}' /proc/net/dev)"
