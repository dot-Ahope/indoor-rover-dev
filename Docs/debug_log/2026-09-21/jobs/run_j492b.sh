#!/bin/bash
# 읽기 전용: lookupInSlice 구현·슬라이스 origin 계산·절단 기본값
H=${JETSON_HOST:-192.168.0.101}; O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=10"
timeout 60 sshpass -p <PW> ssh $O jetson@$H 'R=/home/jetson/workspaces/isaac_ros-dev/src/isaac_ros_nvblox
F=$R/nvblox_nav2/src/nvblox_costmap_layer.cpp; echo "## lookupInSlice"; grep -n "" $F | sed -n "/::lookupInSlice/,/^[0-9]*:}/p" | grep -vE "^[0-9]+:\s*$"
echo "## converter files"; find $R -name "*slice*conver*" | head; 
for f in $(find $R -name "esdf_slice_converter*.cpp" -o -name "esdf_slice_converter*.cu" | head -3); do echo "## $f origin"; grep -n "origin\|aabb\|min_corner\|resolution" $f | head -20; done
echo "## truncation defaults"; grep -rn "truncation_distance_vox" $R --include=*.yaml --include=*.hpp --include=*.h --include=*.cpp -l | head -8; grep -rn "truncation_distance_vox" $R --include=*.yaml | head -6
echo "## 실행 중 nvblox 파라미터 파일"; grep -n "truncation\|voxel_size\|esdf_slice\|max_site\|min_weight" /tmp/nvblox_n0.yaml /home/jetson/nvblox_n0.yaml 2>/dev/null | head -12'
