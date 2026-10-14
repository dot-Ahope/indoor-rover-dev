#!/bin/bash
# (10-14 §18) pad_relief 가 한 번 내렸다 올린 뒤의 로컬 코스트맵 상태(스택 그대로) — 로버 안 움직임
export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash
g() { timeout 12 ros2 param get $1 $2 2>&1 | tail -1 | sed 's/.*is: //' | cut -c1-120; }
for n in /local_costmap/local_costmap /global_costmap/global_costmap; do echo "$n: padding $(g $n footprint_padding) · footprint $(g $n footprint) · inflation r $(g $n inflation_layer.inflation_radius) k $(g $n inflation_layer.cost_scaling_factor)"; done
echo "published_footprint(local): $(timeout 8 ros2 topic echo --once /local_costmap/published_footprint 2>/dev/null | grep -A1 ' x:\| y:' | grep -o '[-0-9.]*' | tr '\n' ' ' | cut -c1-200)"
grep -a "local_costmap" /tmp/nav2.log | grep -a -i "footprint\|padding\|reset\|inflat\|param" | tail -8 | cut -c1-200
