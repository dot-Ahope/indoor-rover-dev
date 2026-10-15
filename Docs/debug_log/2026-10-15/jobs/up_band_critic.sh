#!/bin/bash
# (10-15 §29) ClearanceBandCritic 배포 + 빌드 — /tmp/cbc.tar 를 src 에 풀고(바뀌는 원본은 날짜 붙여 백업) colcon 빌드. 로버 안 움직임
D=~/ros2_ws/src/rover_navigation; T=$(date +%m%d_%H%M%S); mkdir -p /tmp/cbc_x && rm -rf /tmp/cbc_x/* && tar xf /tmp/cbc.tar -C /tmp/cbc_x
for f in CMakeLists.txt package.xml config/nav2_params.yaml; do cp -p $D/$f $D/$f.bak_$T; done
cp /tmp/cbc_x/clearance_band_critic.cpp $D/src/; cp /tmp/cbc_x/mppi_critic_plugins.xml /tmp/cbc_x/CMakeLists.txt /tmp/cbc_x/package.xml $D/; cp /tmp/cbc_x/nav2_params.yaml $D/config/
for f in $D/CMakeLists.txt $D/package.xml $D/config/nav2_params.yaml $D/src/clearance_band_critic.cpp $D/mppi_critic_plugins.xml; do sed -i 's/\r$//' $f; done
echo "백업 접미사 .bak_$T"
export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash
cd ~/ros2_ws && colcon build --symlink-install --packages-select rover_navigation 2>&1 | tail -25
ls -la ~/ros2_ws/install/rover_navigation/lib/librover_clearance_band_critic.so 2>&1
cat ~/ros2_ws/install/rover_navigation/share/ament_index/resource_index/nav2_mppi_controller__pluginlib__plugin/rover_navigation 2>&1
