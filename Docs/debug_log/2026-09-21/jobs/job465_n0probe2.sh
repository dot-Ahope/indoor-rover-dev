#!/bin/bash
echo "== 루트 디스크: $(findmnt -n -o SOURCE /) | $(lsblk -d -o NAME,TYPE,SIZE,ROTA,MODEL 2>/dev/null | grep -E 'nvme|mmcblk|sd' | tr '\n' ';')"
echo "== git-lfs: $(command -v git-lfs || echo 없음) $(git lfs version 2>/dev/null | cut -c1-40) | git: $(git --version)"
echo "== ISAAC_ROS_WS in bashrc: $(grep -c ISAAC_ROS_WS ~/.bashrc) | ~/workspaces: $(ls -d ~/workspaces 2>/dev/null || echo 없음)"
echo "== /dev/shm: $(df -h /dev/shm | tail -1 | awk '{print $2" 중 "$3" 사용"}') | daemon.json: $(cat /etc/docker/daemon.json 2>/dev/null | tr -d '\n ' | cut -c1-160)"
echo "== docker 익명 풀 시험(작은 공개 이미지, nvcr.io): "; timeout 60 docker pull nvcr.io/nvidia/cuda:12.6.0-base-ubuntu22.04 2>&1 | tail -1 | cut -c1-120; docker rmi nvcr.io/nvidia/cuda:12.6.0-base-ubuntu22.04 >/dev/null 2>&1
echo "== 카메라 토픽(깊이 이미지·camera_info 존재?): $(timeout 8 ros2 topic list 2>/dev/null | grep -E 'depth/image_rect_raw|depth/camera_info|color/image_raw' | tr '\n' ' ')"
echo "== 온도/전원 지금: $(cat /sys/devices/virtual/thermal/thermal_zone0/temp) | nvpmodel $(nvpmodel -q 2>/dev/null | head -1)"
