#!/bin/bash
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "=== 1) 전역·로컬 코스트맵 초기화 직후 질의 ==="
timeout 15 ros2 service call /global_costmap/clear_entirely_global_costmap nav2_msgs/srv/ClearEntireCostmap "{}" >/dev/null 2>&1
timeout 15 ros2 service call /local_costmap/clear_entirely_local_costmap nav2_msgs/srv/ClearEntireCostmap "{}" >/dev/null 2>&1
sleep 2
python3 /tmp/job64c_globaldiag.py 2>/dev/null | sed -n '4,16p'
python3 /tmp/job63_planquery.py 1.6 0 0 2>&1 | tail -4
echo
echo "=== 2) depth 소스를 전역에서 배제(마킹 높이 범위 0) 후 재질의 ==="
timeout 10 ros2 param set /global_costmap/global_costmap voxel_layer.depth.min_obstacle_height 5.0 >/dev/null 2>&1
timeout 15 ros2 service call /global_costmap/clear_entirely_global_costmap nav2_msgs/srv/ClearEntireCostmap "{}" >/dev/null 2>&1
sleep 3
python3 /tmp/job64c_globaldiag.py 2>/dev/null | sed -n '4,16p'
python3 /tmp/job63_planquery.py 1.6 0 0 2>&1 | tail -4
