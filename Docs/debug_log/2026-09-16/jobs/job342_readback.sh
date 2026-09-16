#!/bin/bash
source /opt/ros/humble/setup.bash
for p in controller_frequency FollowPathMPPI.model_dt FollowPathMPPI.time_steps FollowPathMPPI.visualize; do printf "  %-34s " $p; timeout 8 ros2 param get /controller_server $p 2>&1 | tail -1; done
printf "  %-34s " local.voxel_decay; timeout 8 ros2 param get /local_costmap/local_costmap stvl_layer.voxel_decay 2>&1 | tail -1
printf "  %-34s " global.voxel_decay; timeout 8 ros2 param get /global_costmap/global_costmap stvl_layer.voxel_decay 2>&1 | tail -1
printf "  %-34s " relay.max_range; timeout 8 ros2 param get /depth_relay max_range 2>&1 | tail -1
echo "  relay CPU: $(top -bn1 | grep -a depth_relay | awk '{print $9}' | head -1) %   load: $(cut -d' ' -f1-3 /proc/loadavg)"
echo "  BT: $(grep -o 'controller_id="FollowPathMPPI"' ~/ros2_ws/install/rover_navigation/share/rover_navigation/config/nav_to_pose_no_spin.xml | head -1)"
