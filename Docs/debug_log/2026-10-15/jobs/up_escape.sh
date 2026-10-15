#!/bin/bash
# (10-15 §26) MonotoneEscape 배포 + 빌드 — /tmp/esc.tar 를 src 에 풀고(바뀌는 원본은 날짜 붙여 백업) colcon 빌드. 로버 안 움직임
set -e
D=~/ros2_ws/src/rover_navigation; T=$(date +%m%d_%H%M%S); mkdir -p /tmp/esc_x && rm -rf /tmp/esc_x/* && tar xf /tmp/esc.tar -C /tmp/esc_x
for f in CMakeLists.txt package.xml config/nav2_params.yaml config/nav_to_pose_no_spin.xml config/nvblox_local.yaml; do cp -p $D/$f $D/$f.bak_$T; done
mkdir -p $D/src
cp /tmp/esc_x/monotone_escape_behavior.cpp $D/src/; cp /tmp/esc_x/behavior_plugins.xml $D/; cp /tmp/esc_x/CMakeLists.txt /tmp/esc_x/package.xml $D/
cp /tmp/esc_x/nav2_params.yaml /tmp/esc_x/nav_to_pose_no_spin.xml /tmp/esc_x/nvblox_local.yaml $D/config/
for f in $D/CMakeLists.txt $D/package.xml $D/config/*.yaml $D/config/*.xml $D/src/*.cpp $D/behavior_plugins.xml; do sed -i 's/\r$//' $f; done
echo "백업 접미사 .bak_$T"
set +e
export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash
cd ~/ros2_ws && colcon build --symlink-install --packages-select rover_navigation 2>&1 | tail -25
echo "빌드 결과: $?"; ls -la ~/ros2_ws/install/rover_navigation/lib/librover_monotone_escape_behavior.so 2>&1
grep -c monotone ~/ros2_ws/install/rover_navigation/share/ament_index/resource_index/nav2_core__pluginlib__plugin/rover_navigation 2>/dev/null || ls ~/ros2_ws/install/rover_navigation/share/ament_index/resource_index/ | head
