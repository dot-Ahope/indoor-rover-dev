#!/bin/bash
CN=isaac_ros_dev-aarch64-container
echo "설치 yaml: $(grep -a 'esdf_slice_min_height' ~/ros2_ws/install/rover_navigation/share/rover_navigation/config/nvblox_local.yaml | cut -c1-60) | 활성 사본: $(grep -a 'esdf_slice_min_height' /tmp/nvblox_active.yaml | cut -c1-60)"
echo "실효값: $(docker exec -u admin $CN bash -lc 'export FASTRTPS_DEFAULT_PROFILES_FILE=/tmp/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; timeout 12 ros2 param get /nvblox_node static_mapper.esdf_slice_min_height 2>&1 | tail -1; timeout 12 ros2 param get /nvblox_node static_mapper.esdf_slice_height 2>&1 | tail -1' | tr '\n' ' ')"
echo "노드 기동 시각: $(docker exec $CN bash -c "ps -o etimes=,cmd= -p \$(pgrep -f '^/opt/ros/humble/lib/nvblox_ros/nvblox_node' | head -1)" | cut -c1-60)"
