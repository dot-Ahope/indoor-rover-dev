#!/bin/bash
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
for h in 0.15 0.10 0.06; do
  timeout 10 ros2 param set /local_costmap/local_costmap voxel_layer.depth.min_obstacle_height $h > /dev/null 2>&1
  timeout 15 ros2 service call /local_costmap/clear_entirely_local_costmap nav2_msgs/srv/ClearEntireCostmap "{}" > /dev/null 2>&1
  sleep 5
  echo "== depth.min_obstacle_height = $h =="; python3 /tmp/job59g_costchk.py | tail -4
done
echo "== depth 소스를 끄고(clearing/marking 유지, 라이다만) =="
timeout 10 ros2 param set /local_costmap/local_costmap voxel_layer.depth.max_obstacle_height 0.0 > /dev/null 2>&1
timeout 15 ros2 service call /local_costmap/clear_entirely_local_costmap nav2_msgs/srv/ClearEntireCostmap "{}" > /dev/null 2>&1; sleep 5
python3 /tmp/job59g_costchk.py | tail -4
timeout 10 ros2 param set /local_costmap/local_costmap voxel_layer.depth.max_obstacle_height 0.40 > /dev/null 2>&1
