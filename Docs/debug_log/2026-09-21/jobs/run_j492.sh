#!/bin/bash
# 읽기 전용: nvblox_nav2 층의 거리→비용 변환·격자 조회 코드와 슬라이스 origin 규약 확인 (DDS 참여 없음)
H=${JETSON_HOST:-192.168.0.101}; O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=10"
timeout 60 sshpass -p <PW> ssh $O jetson@$H 'R=/home/jetson/workspaces/isaac_ros-dev/src/isaac_ros_nvblox
F=$R/nvblox_nav2/src/nvblox_costmap_layer.cpp; echo "## $F"; grep -n "" $F | sed -n "/updateCosts\|updateBounds/,\$p" | grep -vE "^\s*[0-9]+:\s*$|^[0-9]+:\s*//" | head -120
echo "## msg"; cat $R/nvblox_msgs/msg/DistanceMapSlice.msg
echo "## converter origin"; grep -rn "origin" $R/nvblox_ros/src/conversions/esdf_slice_converter.cpp $R/nvblox_ros/include/nvblox_ros/conversions/esdf_slice_converter.hpp 2>/dev/null | head -20
echo "## truncation params"; grep -rn "truncation_distance_vox\|esdf_integrator_max_site_distance_vox\|esdf_integrator_min_weight" $R/nvblox_ros/config/nvblox/*.yaml $R/nvblox_ros/config/nvblox/specializations/*.yaml 2>/dev/null | head -12'
