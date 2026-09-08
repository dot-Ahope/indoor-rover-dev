#!/bin/bash
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
timeout 10 ros2 param set /local_costmap/local_costmap inflation_layer.inflation_radius 0.40 >/dev/null 2>&1
timeout 10 ros2 param set /global_costmap/global_costmap inflation_layer.inflation_radius 0.35 >/dev/null 2>&1
echo -n "  로컬 inflation="; timeout 8 ros2 param get /local_costmap/local_costmap inflation_layer.inflation_radius 2>&1 | grep -oE "[0-9.]+$"
echo -n "  전역 inflation="; timeout 8 ros2 param get /global_costmap/global_costmap inflation_layer.inflation_radius 2>&1 | grep -oE "[0-9.]+$"
echo -n "  패딩="; timeout 8 ros2 param get /local_costmap/local_costmap footprint_padding 2>&1 | grep -oE "[0-9.]+$"
timeout 15 ros2 service call /global_costmap/clear_entirely_global_costmap nav2_msgs/srv/ClearEntireCostmap "{}" >/dev/null 2>&1
timeout 15 ros2 service call /local_costmap/clear_entirely_local_costmap nav2_msgs/srv/ClearEntireCostmap "{}" >/dev/null 2>&1
sleep 5; python3 /tmp/job73_probe.py | head -1
