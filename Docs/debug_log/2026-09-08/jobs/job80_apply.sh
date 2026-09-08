#!/bin/bash
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
timeout 10 ros2 param set /global_costmap/global_costmap voxel_layer.depth.raytrace_min_range 0.30 >/dev/null 2>&1
timeout 15 ros2 service call /global_costmap/clear_entirely_global_costmap nav2_msgs/srv/ClearEntireCostmap "{}" >/dev/null 2>&1
timeout 15 ros2 service call /local_costmap/clear_entirely_local_costmap nav2_msgs/srv/ClearEntireCostmap "{}" >/dev/null 2>&1
sleep 6
echo -n "전역 raytrace_min: "; timeout 8 ros2 param get /global_costmap/global_costmap voxel_layer.depth.raytrace_min_range 2>&1 | tail -1
echo -n "로컬 raytrace_min: "; timeout 8 ros2 param get /local_costmap/local_costmap voxel_layer.depth.raytrace_min_range 2>&1 | tail -1
echo "== 전역 코스트맵 (초기화 후) =="; python3 /tmp/job64e_map.py 2>/dev/null | sed -n '3,14p'
