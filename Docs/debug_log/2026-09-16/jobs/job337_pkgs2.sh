#!/bin/bash
source /opt/ros/humble/setup.bash
L=$(ros2 pkg list 2>/dev/null)
for p in nav2_navfn_planner nav2_theta_star_planner nav2_smoother nav2_constrained_smoother nav2_rotation_shim_controller nav2_dwb_controller nav2_mppi_controller nav2_smac_planner; do
  printf "%-32s %s\n" "$p" "$(echo "$L" | grep -c "^$p\$")"
done
echo "apt 후보: $(apt-cache policy ros-humble-nav2-theta-star-planner 2>/dev/null | grep -aE 'Candidate' | head -1)"
