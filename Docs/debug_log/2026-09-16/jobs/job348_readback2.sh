#!/bin/bash
source /opt/ros/humble/setup.bash
for i in $(seq 1 12); do timeout 5 ros2 param get /controller_server controller_frequency >/dev/null 2>&1 && break; sleep 3; done
for p in controller_frequency FollowPathMPPI.model_dt FollowPathMPPI.time_steps FollowPathMPPI.temperature FollowPathMPPI.iteration_count FollowPathMPPI.vx_std FollowPathMPPI.wz_std FollowPathMPPI.visualize; do printf "  %-34s %s\n" $p "$(timeout 8 ros2 param get /controller_server $p 2>&1 | tail -1)"; done
X=~/ros2_ws/install/rover_navigation/share/rover_navigation/config/nav_to_pose_no_spin.xml
echo "  BT raw_path: $(grep -c raw_path $X)  SmoothPath: $(grep -c '<SmoothPath' $X)"
echo "  nav2: controller $(pgrep -fc controller_server) planner $(pgrep -fc planner_server) bt $(pgrep -fc bt_navigator) stuck_monitor $(pgrep -fc stuck_monitor)"
echo "  stuck_monitor 파라미터: $(timeout 8 ros2 param list /stuck_monitor 2>/dev/null | tr '\n' ' ' | cut -c1-200)"
for p in shadow stuck_shadow ratio_threshold min_cmd_dist window_sec; do v=$(timeout 6 ros2 param get /stuck_monitor $p 2>&1 | tail -1); echo "    $p: $v"; done
printf "  로버 자세: "; timeout 8 ros2 run tf2_ros tf2_echo map base_link 2>&1 | grep -aE "Translation|RPY" | head -2 | tr '\n' ' '; echo
