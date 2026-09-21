#!/bin/bash
# 읽기 전용: 슬라이스 origin 이 픽셀 모서리인지 중심인지 (esdf_slice_conversions.cu)
H=${JETSON_HOST:-192.168.0.101}; O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=10"
timeout 60 sshpass -p <PW> ssh $O jetson@$H 'R=/home/jetson/workspaces/isaac_ros-dev/src/isaac_ros_nvblox
F=$R/nvblox_ros/src/lib/conversions/esdf_slice_conversions.cu; grep -n "origin\|aabb\|min()\|width\|height\|resolution\|0.5" $F | head -40
echo "## nvblox core slice image origin"; grep -rn "min_corner\|origin\|0.5f" /opt/ros/humble/include/nvblox/nvblox/mapper/*slice* /opt/ros/humble/include/nvblox/nvblox/integrators/esdf_slicer.h 2>/dev/null | head -12
G=$(find / -name "esdf_slicer*" 2>/dev/null | head -3); echo "## slicer files: $G"'
