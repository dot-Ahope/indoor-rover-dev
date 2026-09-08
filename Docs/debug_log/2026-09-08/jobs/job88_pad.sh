#!/bin/bash
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
for cm in local_costmap global_costmap; do
  timeout 10 ros2 param set /$cm/$cm footprint_padding 0.02 >/dev/null 2>&1
  echo -n "  $cm padding="; timeout 8 ros2 param get /$cm/$cm footprint_padding 2>&1 | grep -oE "[0-9.]+$"
done
timeout 15 ros2 service call /global_costmap/clear_entirely_global_costmap nav2_msgs/srv/ClearEntireCostmap "{}" >/dev/null 2>&1
timeout 15 ros2 service call /local_costmap/clear_entirely_local_costmap nav2_msgs/srv/ClearEntireCostmap "{}" >/dev/null 2>&1
sleep 5
python3 /tmp/job73_probe.py | tail -2
