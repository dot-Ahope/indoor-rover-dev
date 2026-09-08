#!/bin/bash
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
for cm in local_costmap global_costmap; do
  timeout 10 ros2 param set /$cm/$cm voxel_layer.mark_threshold 0 >/dev/null 2>&1
  timeout 10 ros2 param set /$cm/$cm voxel_layer.depth.min_obstacle_height 0.06 >/dev/null 2>&1
  echo -n "  $cm mark_threshold="; timeout 8 ros2 param get /$cm/$cm voxel_layer.mark_threshold 2>&1 | grep -oE "[0-9]+$"
  echo -n "  $cm depth.min_h="; timeout 8 ros2 param get /$cm/$cm voxel_layer.depth.min_obstacle_height 2>&1 | grep -oE "[0-9.]+$"
done
timeout 15 ros2 service call /global_costmap/clear_entirely_global_costmap nav2_msgs/srv/ClearEntireCostmap "{}" >/dev/null 2>&1
timeout 15 ros2 service call /local_costmap/clear_entirely_local_costmap nav2_msgs/srv/ClearEntireCostmap "{}" >/dev/null 2>&1
sleep 5
echo "== 현재 장면 =="; python3 /tmp/job73_probe.py
