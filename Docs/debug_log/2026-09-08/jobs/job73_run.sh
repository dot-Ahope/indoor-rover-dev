#!/bin/bash
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "=== 현재 상태 ==="; python3 /tmp/job73_probe.py
echo
echo "=== 전역 depth min_obstacle_height 를 -1.0 으로 낮추고 재확인 ==="
timeout 10 ros2 param set /global_costmap/global_costmap voxel_layer.depth.min_obstacle_height -1.0 >/dev/null 2>&1
timeout 15 ros2 service call /global_costmap/clear_entirely_global_costmap nav2_msgs/srv/ClearEntireCostmap "{}" >/dev/null 2>&1
sleep 6; python3 /tmp/job73_probe.py
echo
echo "=== 전역 depth obstacle_max_range 를 3.0 으로 올리고 재확인 ==="
timeout 10 ros2 param set /global_costmap/global_costmap voxel_layer.depth.obstacle_max_range 3.0 >/dev/null 2>&1
timeout 15 ros2 service call /global_costmap/clear_entirely_global_costmap nav2_msgs/srv/ClearEntireCostmap "{}" >/dev/null 2>&1
sleep 6; python3 /tmp/job73_probe.py
