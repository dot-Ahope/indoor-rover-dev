#!/bin/bash
SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
OPT="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=15"
J=jetson@192.168.0.101
echo "=== 릴레이 ==="; bash $SPS/run_j.sh job314_relay_orphan.sh 2>&1 | grep -aE '남은 릴레이|발행자|out hz'
echo "=== readback ==="
sshpass -p <PW> ssh $OPT $J "source /opt/ros/humble/setup.bash; for n in /local_costmap/local_costmap /global_costmap/global_costmap; do printf '%-32s padding ' \$n; timeout 8 ros2 param get \$n footprint_padding 2>&1 | tail -1; done; printf 'local decay '; timeout 8 ros2 param get /local_costmap/local_costmap stvl_layer.voxel_decay 2>&1 | tail -1; for p in cost_scaling_dist regulated_linear_scaling_min_speed max_allowed_time_to_collision_up_to_carrot; do printf 'RPP %-42s ' \$p; timeout 8 ros2 param get /controller_server FollowPath.\$p 2>&1 | tail -1; done; for p in minimum_turning_radius cost_penalty non_straight_penalty; do printf 'Smac %-24s ' \$p; timeout 8 ros2 param get /planner_server SmacHybrid.\$p 2>&1 | tail -1; done; printf 'BT '; grep -oE 'planner_id=\"[A-Za-z]+\"/>' ~/ros2_ws/install/rover_navigation/share/rover_navigation/config/nav_to_pose_no_spin.xml; grep -a '프레임:' /tmp/sensors.log | tail -1 | grep -aoE '입력.*'; uptime | grep -aoE 'load average.*'"
