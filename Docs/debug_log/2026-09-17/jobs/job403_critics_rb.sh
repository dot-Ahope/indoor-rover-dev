#!/bin/bash
export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml
source /opt/ros/humble/setup.bash
for p in GoalCritic.cost_weight PathFollowCritic.threshold_to_consider PathAlignCritic.threshold_to_consider PathAngleCritic.threshold_to_consider PathFollowCritic.cost_weight PathFollowCritic.offset_from_furthest visualize; do printf "  %-42s %s\n" FollowPathMPPI.$p "$(timeout 8 ros2 param get /controller_server FollowPathMPPI.$p 2>&1 | tail -1)"; done
printf "  %-42s %s\n" bt.default_server_timeout "$(timeout 8 ros2 param get /bt_navigator default_server_timeout 2>&1 | tail -1)"
python3 /tmp/job386_slamalive.py 2>&1 | grep -av '^\['
python3 /tmp/job377_goalclear.py 2.0 0.0 2>&1 | grep -a "목표 map"
printf "  battery: "; timeout 6 ros2 topic echo /battery --once 2>/dev/null | grep -aoE 'voltage: [0-9.]+'
