#!/bin/bash
export FASTRTPS_DEFAULT_PROFILES_FILE=$HOME/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
for tp in /camera/depth/points_filtered /plan_smoothed /unsmoothed_plan /local_costmap/costmap_raw; do
  echo "-- $tp: $(timeout 14 ros2 topic bw --window 20 $tp 2>/dev/null | grep -aE 'average|from' | tail -2 | tr '\n' ' ' | cut -c1-150)"
done
echo "-- hz points_filtered: $(timeout 10 ros2 topic hz --window 20 /camera/depth/points_filtered 2>/dev/null | grep -a average | tail -1)"
