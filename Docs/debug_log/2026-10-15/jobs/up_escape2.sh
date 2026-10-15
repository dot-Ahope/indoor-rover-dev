#!/bin/bash
# (10-15 §26) package.xml 중복 의존 고친 판만 다시 배포 + 빌드. 로버 안 움직임
D=~/ros2_ws/src/rover_navigation; tr -d '\r' < /tmp/package.xml > $D/package.xml
export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash
cd ~/ros2_ws && colcon build --symlink-install --packages-select rover_navigation 2>&1 | grep -v "^$" | tail -20
ls -la ~/ros2_ws/install/rover_navigation/lib/librover_monotone_escape_behavior.so 2>&1
cat ~/ros2_ws/install/rover_navigation/share/ament_index/resource_index/nav2_core__pluginlib__plugin/rover_navigation 2>&1
